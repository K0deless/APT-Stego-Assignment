#!/usr/bin/python3

'''
Python tool to hide information inside of text through a key.

File: text_stego.py

@authors:
    - David Regueira
    - Santiago Rocha
    - Eduardo Blazquez
    - Jorge Sanchez
'''

""" Implementation of the algorithms for other parts of the tool """


##########IMPORTANT NOTE##########
##Libmagic dependencies must be installed on system
##-Check https://pypi.org/project/python-magic/ for more information
import string, mimetypes, magic, os
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngImageFile, PngInfo


class NotValidTextException(Exception):
    """ Given text where to hide info, not good enough """
    pass

class InvalidBitValue(Exception):
    """ Really weird exception, bit is not a bit """
    pass

class InvalidCharacter(Exception):
    """ Found a character on key not present on text """
    pass

class ParagraphsHiding():
    """ Approach based on key to hide a message inside of a given text (based on point 3.3 of [Agarwal, 2013]) """

    def __init__(self, file_where_to_hide, file_to_hide = '', key = '', file_to_unhide = ''):
        """
        Constructor of the class ParagraphsHiding,
        we will assign variables and clean words
        from the text.

        :param file_where_to_hide: file with the text where to hide the information.
        :param file_to_hide: optional, file with the information to hide.
        :param key: optional, string with the key to use for unhidding.
        :param file_to_unhide: optional, file where to write unhidden information.
        """
        self.file_where_to_hide = file_where_to_hide
        self.file_to_hide = file_to_hide
        self.file_to_unhide = file_to_unhide
        self.key = key
        self.text = ""
        self.clean_words = []

        self.byte_array_to_hide = None

        if not os.path.exists(file_where_to_hide):
            raise FileNotFoundError("%s file where to hide does not exists" % (file_where_to_hide))

        if file_to_hide != '':
            if not os.path.exists(file_to_hide):
                raise FileNotFoundError("%s file to hide does not exists" % (file_to_hide))
            self.byte_array_to_hide = np.fromfile(self.file_to_hide, dtype = "uint8")
        

        self.__clean_words()

    def __clean_words(self):
        """
        Internal method to clean the given text,
        allowed words will be only those that
        are 'alpha' words without numbers. It also
        removes non ascii characters
        """
        with open(self.file_where_to_hide,'r') as file_:
            self.text = file_.read()

        # first remove punctuation marks on text
        clean_text = self.text.translate(str.maketrans(
            string.punctuation, ' ' * len(string.punctuation)))

        # remove non ascii characters from words
        #clean_text = "".join(i for i in clean_text if ord(i)<128)

        # remove those words with just 1 letter
        # and those that include numbers
        self.clean_words = [
            i for i in clean_text.split() if len(i) > 1 and i.isalpha() and i[0] != i[-1]]


    def hide_information(self):
        """
        Method to get a key derived from hiding
        the given message into the given text.

        :return: str with generated key.
        """
        index_word = 0
        key = ""
        # go through the hole message
        for bit in np.unpackbits(self.byte_array_to_hide):
            if bit == 0:
                key += self.clean_words[index_word][-1]
            elif bit == 1:
                key += self.clean_words[index_word][0]
            else:
                raise InvalidBitValue("hide_information: (numpy.unpackbits) Unknown value for bit %d" % (bit))

            index_word += 1
            # use text where to hide a cyclic way
            if index_word == len(self.clean_words):
                index_word = 0
        
        return key

    def unhide_information(self):
        """
        Method to extract the information from the
        given text, using the key to know which
        information to extract.

        :return: str with extracted filename
        """
        index_word = 0

        bits_list = []
        
        for c in self.key:
            if c == self.clean_words[index_word][0]:
                bits_list.append(1)
            elif c == self.clean_words[index_word][-1]:
                bits_list.append(0)
            else:
                raise InvalidCharacter("unhide_information: Character mismatch in word %c" % (c))

            index_word += 1
            # use text where to unhide a cyclic way
            if index_word == len(self.clean_words):
                index_word = 0

        file_content = np.packbits(bits_list)
        
        mime = magic.from_buffer(file_content.tostring(), mime=True)
        if mime == 'text/plain': 
            extension = '.txt'
        else:
            extension = mimetypes.guess_extension(mime)

        f_name = "{}{}".format(self.file_to_unhide, extension)

        with open(f_name,'wb') as file_:
            file_content = np.packbits(bits_list)
            file_content.tofile(file_)

        return f_name

class ImageHiding():
    """ Approach based on RGB pixel values to hide text data across an Image """

    def __init__(self, image_where_to_hide, key_to_hide = '', url_metadata = '', url_language = ''):
        """
        Constructor of the class ImageHiding.
        If key is provided, it will be hidden into the image,
        either way it will be recovered.

        :param image_where_to_hide: image where to hide the information.
        :param key_to_hide: optional, key to hide into the image.
        """
        self.image_where_to_hide = image_where_to_hide
        self.key_to_hide = key_to_hide
        self.url_metadata = url_metadata
        self.url_language = url_language

        if self.image_where_to_hide != '':
            #open image and made a copy to work with
            self.image_object = Image.open(self.image_where_to_hide, 'r')

            #check if image is valid for stego
            if self.image_object.mode not in ('RGB', 'RGBA', 'CMYK'):
                raise ValueError('Unsupported pixel format: image must be RGB, RGBA, or CMYK')
            if self.image_object.format == 'JPEG':
                raise ValueError('JPEG format incompatible with steganography')


    def hide_information(self):
        """
        Method to hide a key 
        into the given image
        """
        
        #first of all is to change original cover file metadata
        #because if we do it later, bits will be changed and key 
        # will not be recovered

        _tmp_image = self.image_object.copy()

        max_with = _tmp_image.size[0] - 1
        (coord_x, coord_y) = (0, 0)

        for pixel in self.encode_imdata(_tmp_image.getdata(), self.key_to_hide):
            _tmp_image.putpixel((coord_x, coord_y), pixel)
            if (coord_x == max_with):
                coord_x = 0
                coord_y += 1
            else:
                coord_x += 1

        #save the resulting image
        #image_format = self.image_where_to_hide.split(".")[1]
        image_format = "png"
        f_name = self.image_where_to_hide.split(".")[0]+"_hide." + image_format

        metadata = PngInfo()
        metadata.add_text("url", self.url_metadata)
        metadata.add_text("language", self.url_language)

        _tmp_image.save(f_name, image_format.upper(), pnginfo=metadata)


    def unhide_information(self):
        """
        Method to extract a key from the given image.

        :return: str with the key or empty if error
        :return: str with the url to fetch the cover text
        """

        key = ''
        _image_data = iter(self.image_object.getdata())

        while True:
            #get RGB values from 3 pixels of the image
            rgb_values = list(_image_data.__next__()[:3] + 
                              _image_data.__next__()[:3] + 
                              _image_data.__next__()[:3]) 

            char_byte = 0
            #recover char from pixels changed bits
            for bit_index in range(7):
                char_byte |= rgb_values[bit_index] & 1
                char_byte <<= 1
            char_byte |= rgb_values[7] & 1

            #convert 8 bit string to char
            key += chr(char_byte)

            if rgb_values[-1] & 1:
                break

        url, language = self.recover_metadata()
        return key, url, language
                

    def recover_metadata(self):
        url_image = PngImageFile(self.image_where_to_hide)

        return url_image.text["url"], url_image.text["language"]

    def encode_imdata(self, image_data, key):
        '''given a sequence of pixels, returns an iterator of pixels with
        encoded data'''

        len_key = len(key)
        if len_key == 0:
            raise ValueError('data is empty')
        if len_key * 3 > len(image_data):
            raise ValueError('data is too large for image')

        _image_data = iter(image_data)

        for char_index in range(len_key):
            #get RGB values from 3 pixels of the image
            rgb_values = [value & ~1 for value in _image_data.__next__()[:3] + 
                                              _image_data.__next__()[:3] + 
                                              _image_data.__next__()[:3]]
            
            #pixel value is converted to even if bit is 0 and odd if bit is 1
            char_byte = ord(key[char_index])
            for bit_index in range(7, -1, -1):
                rgb_values[bit_index] |= char_byte & 1
                char_byte >>= 1

            #eight pixel of every set tells to stop or read more.
            #1 means keep reading and 0 means message finished,
            #following the same approach as before with odd and even
            if char_index == len_key - 1:
                rgb_values[-1] |= 1

            pixels = tuple(rgb_values)

            yield pixels[0:3]
            yield pixels[3:6]
            yield pixels[6:9]


if __name__ == '__main__':
    '''
    try:
        import crawler
        source = crawler.SourceFinding(source_language="es")
        url, source = source.generate()

        print("Cover fetched from: %s" % url)

        ph = ParagraphsHiding('cover.txt', file_to_hide='secret.txt')
        key = ph.hide_information()
        print("File to hide: %s" % ('secret.txt'))
        print("Key: %s" % (key))

        ih = ImageHiding('cover.png', key_to_hide=key, url_metadata=url, url_language=source)
        ih.hide_information()
        print("Key hidden in cover_hide.png")

        uh = ImageHiding('cover_hide.png')
        key, url, language = uh.unhide_information()
        print("Recovered URL: %s (language: %s)" % (url, language))
        print("Recovered key: %s" % key)

        
        uSource = crawler.SourceFinding()
        if language == "es":
            uSource.get_source_es(url)
        elif language == "en":
            uSource.get_source_en(url)
        else:
            uSource.get_source_ru(url)


        dh = ParagraphsHiding('cover.txt',key=key, file_to_unhide='secret_unhide.txt')
        dh.unhide_information()
        print("Key (again): %s" % (key))
        print("File unhidden: %s" % ('secret.txt'))
    except NotValidTextException as ne:
        print(ne)'''