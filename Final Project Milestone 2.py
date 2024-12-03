from drafter import *
from bakery import assert_equal
from dataclasses import dataclass
from PIL import Image as PIL_Image
import tkinter as tk
from tkinter import filedialog
import os

def even_or_odd_bit(number: int) -> str:
    ''' consumes an int and returns a str. If the number passed is odd, 
    this function should return a '1' and if its even, it should return a '0';'''
    if number % 2 == 0:
        return "0"
    else:
        return "1"

def decode_single_char(color_intensities: list[int]) -> str:
    '''consumes a list of integers containing eight color intensities values (Base 10). 
    These color intensities represent a single ascii character as described in the Part 
    A Decoding: Decoding Process page'''
    if len(color_intensities) != 8:
        return ""
    new_colors = ""
    for colors in color_intensities:
        new_colors += even_or_odd_bit(colors) 
    return chr(int(new_colors, 2))
            

def decode_chars(color_intensities: list[int], number_characters: int) -> str:
    '''consumes a list of integers of color intensity values and an integer representing how many characters to decode. 
    gThis function should call decode_single_char for each character that needs to be decoded '''
    decoded = ""
    if len(color_intensities) != (8 * number_characters):
        return None
    for colors in range(number_characters):
        current_position = colors * 8
        decoded += decode_single_char(color_intensities[current_position:current_position + 8])
    return decoded

def get_message_length(color_intensities: list[int], number_characters: int) -> int:
    '''consumes a list of color intensity values and an int representing how many characters are used in the header 
    to represent the rest of the message's length ''' 
    if len(color_intensities) != (8*number_characters):
        return 0
    indexed = (8 * number_characters)
    newlist = color_intensities[:indexed]
    new_intensities = decode_chars(newlist, number_characters)
    return int(new_intensities)

def get_encoded_message(color_intensities: list[int]) -> str:
    '''
    consumes a list of color intensities and returns the hidden message
    '''
    message_length = get_message_length(color_intensities[:24], 3)
    end_line = (8 * message_length) + 24
    decoded_line = decode_chars(color_intensities[24:end_line], message_length)
    if not decoded_line:
        return None
    return decoded_line


def get_color_values(img: PIL_Image, channel_index: int) -> list[int]:
    ''' consumes a Pillow Image and an int representing the channel index of the color values. 
    (0 for red channel, 1 for green channel and 2 for blue channel) 
    and returns a list of integers containing the color intensity values for the specified channel'''
    width = img.size[0]
    length = img.size[1]
    empty_values = []
    iterated_values = range(width)
    iterated_values_length = range(length)
    for x in iterated_values:
        for y in iterated_values_length:
            color = img.getpixel((x,y))
            red = color[0]
            green = color[1]
            blue = color[2]
            if channel_index == 0:
                empty_values.append(red)
            elif channel_index == 1:
                empty_values.append(green)
            elif channel_index == 2:
                empty_values.append(blue) 
    return empty_values

def get_message(max_characters: int) -> str:
    message = input("Input your secret message that is up to " 
                    + str(max_characters) + " characters")
    while len(message) > max_characters:
        print("Message is too long, please type in another message that is less than" 
              + str(max_characters) + " characters")
        message = input("Input your secret message that is up to" + str(max_characters))
    return message

def prepend_header(hidden_message: str) -> str:
    '''consumes a string containing the message that should be hidden 
    in the image file and return the string with the number of characters 
    in the message prepended to the front of the message'''
    length = len(hidden_message)
    new_length = ""
    if length < 10:
        new_length = "00" + str(length)
    elif length >= 100:
        new_length = str(length)
    elif length >= 10:
        new_length = "0" + str(length)
    return new_length + hidden_message
    
def message_to_binary(ascii_characters: str) -> str:
    '''onsumes a string containing ascii characters and returns a string 
    containing the binary representation of the ascii characters'''
    empty_message = ""
    for character in ascii_characters: 
        number = ord(character)
        binary = format(number, '08b')
        empty_message += binary
    return empty_message

def new_color_value(color_intensity: int, single_bit: str) -> int:
    '''onsumes two values: an int representing the original Base 10 color intensity value 
    and a string containing the single bit that is to be hidden. This function will return 
    the new Base 10 color intensity value'''
    if single_bit == "1":
        if color_intensity % 2 == 0:
            color_intensity += 1
    elif single_bit == "0":
        if color_intensity % 2 != 0:
            color_intensity -= 1
    return color_intensity

def hide_bits(image: PIL_Image, bits_string: str) -> PIL_Image:
    """ consumes a Pillow Image and the binary string containing the bits that 
    should be hidden in the image and returns a Pillow Image with the hidden message"""
    newbit = -1
    width, length = image.size
    if len(bits_string) > width * length:
        return None
    for index_x in range(length):
        for index_y in range(width):
            newbit = newbit + 1
            if newbit >= len(bits_string):
                return image
            red, green, blue = image.getpixel((index_x,index_y))
            new_green = new_color_value(green,bits_string[newbit])
            image.putpixel((index_x,index_y), (red,new_green,blue))
    return image

def select_file() -> str:    
    '''
    This function asks user to select a local PNG file
      and returns the file name

    Args:
        None         
    Returns:
        str: the file name
    '''
    root = tk.Tk()
    root.withdraw()

    file_path = tk.filedialog.askopenfilename()

    while (file_path == "" or file_path[-4:] != ".png"):   
        print("Invalid file - must select a PNG file.")
        file_path = tk.filedialog.askopenfilename()

    file_name = os.path.basename(file_path)  #remove path 
    return file_name

 

@dataclass
class State:
    """ The start of the website """
    message: str
    image: PIL_Image
    binary: list[int]


@route
def index(state: State) -> Page:
    """ The main page of the website. """
    return Page(state = state,content = ["Encode or decode?",Button(text = "Encode", url = "/upload_image_to_encode"),
                                       Button(text = "Decode", url = "/upload_encoded_image")])

@route
def upload_image_to_encode(state: State) -> Page:
    """where user uploads the image they want to encode"""
    state.message = ""
    return Page(state, ["Upload your image and add your secret message up to 10 characters",FileUpload("image", accept="image/png"), Button(text = "Encode this image!", url = "/encode_message"),
                        TextBox("user_message",state.message)])
    
    
@route
def encode_message(state: State, image: bytes, user_message: str) -> str:
    '''
    main function for hiding a message in an image file
    Args:
        max_chars (int) -> represents the maximum number of characters allowed to be hidden
    Return:
        str: name of the new file where the message is hidden
    '''    
        
        
        
    """file_name = select_file()    # allows user to pick an image file"""
    
    """image = PIL_Image.open(file_name).convert('RGB')"""  # get RGB Pillow Image format of the image file
 
    # after you have defined:
    #      get_message, prepend_header, message_to_binary   
   
    """users_message = get_message(max_chars)  # lets the user enter a message"""
    
    state.image = PIL_Image.open(io.BytesIO(image)).convert('RGB')
    
    while len(user_message) > 10:
        print("Message is too long, please type in another message that is less than" 
            + str(10) + " characters")
        return Page(state, [Button(text = "Go back", url = "/index")])
        
    
    message_with_header = prepend_header(user_message)  #prepends the header to the users message
     
    binary_string = message_to_binary(message_with_header)  # convert the full message to a binary string    
   
    # after you have defined:
    #      hide_bits, new_color_value
       
    new_image = hide_bits(state.image, binary_string) # encode the message into the image
   
    # save the updated image with a new file name
    """new_file_name = "1_" + file_name # format of 1 + old filename (1 represents green channel)"""  
    """image.save(new_file_name, "PNG")"""
      
    return Page(state, [Image(new_image), Download("Download this image", "encoded_image_1", new_image, "image/png")])    
  

"""@route
def encode(state: State, image: PIL_Image, user_message: str) -> Page:
    "" Where the user uploads an image and encodes a message.""
    encode = encode_message(10, image, user_message)
    return Page(state, [str(encode)])"""

@route
def upload_encoded_image(state: State) -> Page:
    """Where the user uploads their encoded image image"""
    state.message = ""
    return Page(state, ["Upload your encoded image and index",FileUpload("new_image", accept="image/png"),
                        "What color index? (0-2)", TextBox("user_message",state.message),
                        Button("Decode this image with the message!", decode_image)])

@route
def decode_image(state: State, new_image: bytes, user_message: str) -> Page:
    state.image = PIL_Image.open(io.BytesIO(new_image)).convert('RGB')
    color_values = get_color_values(state.image,int(user_message))
    
    message = get_encoded_message(color_values)
    
    return Page(state, [message])

start_server(State("Encode or decode?",None,None))
    



    

