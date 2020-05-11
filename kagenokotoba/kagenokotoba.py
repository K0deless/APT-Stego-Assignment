#!/usr/bin/python3

'''
Python tool to hide information inside of text through a key.

File: main.py

@authors:
    - David Regueira
    - Santiago Rocha
    - Eduardo Blazquez
    - Jorge Sanchez
'''


""" App entry point """

import text_stego, crawler
from art import *
import colorama as cla
import sys, random, signal
from os import name, system, remove
import text_stego as stego

from text_stego import InvalidBitValue, InvalidCharacter

def sigint_handler(signum, frame):
    """ Handler for SIGINT interruption (CTRL+C) """
    print("\n\n")
    print(cla.Fore.RED + "[*]SIGINT received exiting")
    print("[!]Thanks for using the tool")
    sys.exit(0)


def clear_screen():
    """ Different ways from cleaning the screen """
    if name == 'nt': 
        _ = system('cls') 
    else: 
        _ = system('clear')

def banner():
    """ Clean screen and print new banner """
    clear_screen()
    logo = text2art("Kage no Kotoba",font="katakana")
    print(cla.Fore.GREEN + logo)
    logo_text = text2art("Kage no Kotoba - Shadow Words",font="fancy")
    print(cla.Fore.YELLOW + logo_text)
    author_text = text2art("\n\nBy k0deless",font="fancy2")
    print(cla.Fore.BLUE + author_text)
    print("*" * 116 + "\n")

def menu():
    """ Print menu to the user """
    choices = input("""
                      1: Hide information
                      2: Unhide Information
                      3: Quit/Log Out

                      Please enter your choice: """)

    if choices == str(1):
        hideInformation()
    elif choices == str(2):
        unhideInformation()
    elif choices == str(3):
        sys.exit
    else:
        print("You must only select either 1,2 or 3.")
        print("Please try again")
        menu()

def main():
    signal.signal(signal.SIGINT, sigint_handler)
    cla.init(autoreset=True)
    banner()
    menu()


def hideInformation():
    """ Call to stego library to hide message in a text and finally hide key and url in an image """
    clear_screen()
    logo_text = text2art("Hiding information",font="fancy", decoration="barcode")
    print(cla.Fore.YELLOW + logo_text)
    print("*" * 116 + "\n")

    secret_file = input("[*]Enter file to hide: ")

    print("[*]Generating cover files...")
    languages = ["es", "en"]
    source = crawler.SourceFinding(source_language=random.choice(languages))
    url, source = source.generate()
    print("[*]Cover files fetched from: %s" % url)

    try:
        ph = stego.ParagraphsHiding('cover.txt', file_to_hide=secret_file)
        key = ph.hide_information()

        print("[*]File %s hidden using cover text words" % (secret_file))
        print(cla.Fore.LIGHTRED_EX + "[*]Generated Key: %s" % (key))

        ih = stego.ImageHiding('cover.png', key_to_hide=key, url_metadata=url, url_language=source)
        ih.hide_information()
        print(cla.Fore.LIGHTRED_EX + "[*]Stego file generated => cover_hide.png")
    except InvalidBitValue as ibv:
        print(cla.Fore.RED + "[-]Error hidding message in text: %s" % (str(ibv)))
        sys.exit(1)
    except FileNotFoundError as fnf:
        print(cla.Fore.RED + "[-]Error with file hidding message in text: %s" % (str(fnf)))
        sys.exit(1)
    except ValueError as ve:
        print(cla.Fore.RED + "[-]Error of value hiding message in text: %s" % (str(ve)))
        sys.exit(1)
    finally:
        remove("cover.txt")
        remove("cover.png")
        print("[*]Cover files removed!!")


def unhideInformation():
    """ Extract key and download text to unhide the message """
    clear_screen()
    logo_text = text2art("UnHiding information",font="fancy", decoration="barcode")
    print(cla.Fore.YELLOW + logo_text)
    print("*" * 116 + "\n")

    secret_file = input("[*]Enter file to unhide: ")
    target_file = input("[*]Enter result file name (whitout extension): ")

    uh = stego.ImageHiding(secret_file)
    key, url, language = uh.unhide_information()
    print("[*]Recovered URL: %s (language: %s)" % (url, language))
    print(cla.Fore.GREEN + "[*]Recovered key: %s" % key)

    print("[*]enerating cover files from recovered data...")
    uSource = crawler.SourceFinding()
    if language == "es":
        uSource.get_source_es(url)
    elif language == "en":
        uSource.get_source_en(url)
    else:
        uSource.get_source_ru(url)
    print("[*]Cover files fetched from: %s" % url)

    try:
        dh = stego.ParagraphsHiding('cover.txt',key=key, file_to_unhide=target_file)
        f_name = dh.unhide_information()

        print(cla.Fore.GREEN + "[*]File unhidden: %s" % (f_name))

    except InvalidCharacter as ic:
        print(cla.Fore.RED + "[-]Error extracting original message from text: %s" % (str(ic)))
        sys.exit(1)
    except FileNotFoundError as fnf:
        print(cla.Fore.RED + "[-]Error with file extracting original message from text: %s" % (str(fnf)))
        sys.exit(1)
    finally:
        remove("cover.txt")
        remove("cover.png")
        print("[*]Cover files removed!!")

if __name__ == "__main__":
    main()
