"""
This file contains the template for the prompt to be used for injecting the context into the model.

"""

from datetime import datetime
now = datetime.now()

def base_prompt(prompt,context, voter_profile):
    final_prompt = f""" GENERAL INFORMATION : ( today is {now.strftime("%d/%m/%Y %H:%M:%S")}. You are a chatbot with the sole purpose to help voters with 
                        their questions regarding political parties, provided to you in a file containing ideals, poltical standpoints/actions and main issue of
                        the following political parties: [PVV, 50Plus, ChristenUnie, D66, CDA, FVD, PvdD, VVD, SP]. You don't have data on other parties. If questions are asked 
                        about other parties, explain that these parties do not participate in the upcoming Dutch elections.
                        INSTRUCTION : ONLY return an answer, never include PREVIOUS MESSAGE or USER QUESTION! Help the user with their question based on their VOTER PROFILE.
                        When answering the user question, try to match the VOTER PROFILE with the ideals, poltical standpoints/actions and main issue of the political parties. 
                        Weigh the ideals heavier than the political actions when deciding if the political party is a fit to the voter. Weigh the main issue the heaviest. 
                        PREVIOUS MESSAGE : ({context})
                        VOTER_PROFILE:  {voter_profile}
                        USER QUESTION : {prompt} . 
                        WRITE THE ANSWER :"""
    return final_prompt


START_UP_MESSAGE = """
                    "Hi there, I'm **KieswAIzer**! To start things of, I prefer to speak English but I do understand Dutch, don't you worry 😉
                    \n 
                    I was developed to help you in your decision making for the upcoming Dutch Elections.
                    To do this, I read the political manifestos (verkiezingsprogramma's) of all participating parties, trying to understand their goals, ideals etc. etc.
                    \n 
                    👈 I can only help you if you first provide me with your 'voter profile', please write this in the sidebar on the left.
                    After you've done that, you can start to ask questions to help you decide what political party aligns best with your preferences.
                    \n 
                    \n 
                    Some examples of questions to get you going:\n
                    - Welke politieke partij past het beste bij mij?\n
                    - Ik twijfel nog tussen D66 en VVD. Welke partij zou jij mij aanraden en waarom?\n
                    - Why do you think the PVV would be a good fit / would not be a good fit for me?\n
                    etc. etc.
                    """

VOTER_PROFILE_1 = """Mijn naam is Fatima. 
Ik ben moslima. Ik ben 26 jaar en woon in Amsterdam. 
Ik maak mij steeds meer zorgen over de polarisatie in de Nederlandse maatschappij. 
Racisme neemt toe, dat moet stoppen. 
Verder vind ik het belangrijk dat de politieke partij waar ik op ga stemmen net zo hard iets aan de klimaatverandering wilt doen als ik. 
De aarde warmt steeds sneller op, er moeten harde maatregelen komen.
\n 
\n 
Welke politieke partij past het beste bij mij?
"""

VOTER_PROFILE_2 =  """Mijn naam is Jan. 
Ik ben 45 jaar oud en woon op het platteland in Drenthe. 
Ik ben al jarenlang boer en maak me grote zorgen over het stikstofprobleem. 
De regelgeving heeft een negatieve impact op mijn bedrijf en inkomen. 
Daarom overweeg ik om op de BoerenBurgerBeweging (BBB) te stemmen, omdat ze opkomen voor de belangen van boeren.
\n
\n
Ik twijfel nog tussen de BBB en JA21. Welke partij zou jij mij aanraden en waarom?"""

VOTER_PROFILE_3 = """Ik ben Sophie, 32 jaar oud en werkzaam in de technologie-industrie in Eindhoven. 
Mijn belangrijkste zorg is de opkomst van technologische werkloosheid en de impact ervan op de samenleving. 
Ik ben op zoek naar een politieke partij die innovatie en omscholing stimuleert om de banen van de toekomst te creëren. 
Ook maak ik me ernstige zorgen over klimaatverandering en steun ik partijen die streven naar duurzame oplossingen.
\n
\n
Is er een partij die aan al deze eisen voldoet? Zo ja, welke, zo nee, waarom niet?
"""

VOTER_PROFILE_4 = """Ik ben Ahmed, 38 jaar oud en woon in Rotterdam. 
Mijn grootste zorg is de stijgende inflatie en de impact ervan op mijn koopkracht. 
De kosten voor basisbehoeften, zoals voedsel en energie, stijgen snel en het wordt steeds moeilijker om rond te komen.
 Ik zoek naar een politieke partij die concrete maatregelen heeft om de inflatie onder controle te houden en de economie te stabiliseren.
"""

VOTER_PROFILE_5 = """Ik ben Lisa, 29 jaar oud en werk in de gezondheidszorg in Utrecht.
 Mijn prioriteit is de toegankelijkheid van de gezondheidszorg. 
 Ik maak me zorgen over de lange wachtlijsten en de druk op het zorgpersoneel. 
 Ik overweeg te stemmen op partijen die zich inzetten voor meer investeringen in de gezondheidszorg en het verminderen van bureaucratie."""

VOTER_PROFILE_6 = """Ik ben Mark, 50 jaar oud en werk als docent in Amsterdam. 
Mijn grootste zorg is de kwaliteit van het onderwijs. 
Ik vind dat er te veel nadruk wordt gelegd op toetsen en te weinig op de ontwikkeling van creativiteit en kritisch denken bij kinderen. 
Ik zoek naar een politieke partij die de onderwijskwaliteit wil verbeteren en de werkdruk voor leraren wil verminderen."""

