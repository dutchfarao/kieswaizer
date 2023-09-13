"""
This file contains the template for the prompt to be used for injecting the context into the model.

"""

from datetime import datetime
now = datetime.now()

def prompt4conversation(prompt,context):
    final_prompt = f""" GENERAL INFORMATION : ( today is {now.strftime("%d/%m/%Y %H:%M:%S")} ,
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt} . 
                        WRITE THE ANSWER :"""
    return final_prompt


def prompt4Code(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : 
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , THE CORRECT ANSWER CONTAINS CODE YOU ARE OBLIGED TO INSERT IT IN YOUR NEW ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CODE FOR THE ANSWER : ({solution}) 
                        WITHOUT CHANGING ANYTHING OF THE CODE of CORRECT ANSWER , MAKE THE ANSWER MORE DETALIED INCLUDING THE CORRECT CODE :"""
    return final_prompt


def prompt4Context(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : 
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE ,WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CORRECT ANSWER : ({solution}) 
                        WITHOUT CHANGING ANYTHING OF CORRECT ANSWER , MAKE THE ANSWER MORE DETALIED:"""
    return final_prompt
