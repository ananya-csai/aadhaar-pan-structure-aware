# -*- coding: utf-8 -*-
"""Synthetic Indian personal-name corpus with three naming strata.

Every name in this module is a common given name or surname drawn from public
knowledge of Indian naming practice.  Names are recombined at random by the
generator, so a generated record does not correspond to any real person.

Three naming strata are represented, following Section IV-C of the paper:

  SURNAME_LAST : "Ananya Shukla"      - given name followed by a surname
  INITIAL_FIRST: "V. Lakshmi"         - an abbreviated leading token
  MONONYMIC    : "Rajesh"             - a single name, no surname

The stratum matters because the PAN cross-field rule of Section III-B keys on
the surname initial, and the three strata differ in whether a surname is
identifiable at all.  A corpus consisting only of SURNAME_LAST names would make
the permissive and strict variants of (2) behave identically.
"""
from __future__ import annotations

SURNAME_LAST = "surname_last"
INITIAL_FIRST = "initial_first"
MONONYMIC = "mononymic"
STRATA = (SURNAME_LAST, INITIAL_FIRST, MONONYMIC)

# (latin, devanagari)
MALE_GIVEN = [
    ("Aarav", "आरव"), ("Abhishek", "अभिषेक"), ("Aditya", "आदित्य"), ("Akash", "आकाश"),
    ("Amit", "अमित"), ("Anil", "अनिल"), ("Ankit", "अंकित"), ("Arjun", "अर्जुन"),
    ("Arun", "अरुण"), ("Ashish", "आशीष"), ("Bharat", "भरत"), ("Chirag", "चिराग"),
    ("Deepak", "दीपक"), ("Devendra", "देवेंद्र"), ("Dhruv", "ध्रुव"), ("Gaurav", "गौरव"),
    ("Girish", "गिरीश"), ("Harsh", "हर्ष"), ("Ishaan", "ईशान"), ("Jatin", "जतिन"),
    ("Kabir", "कबीर"), ("Karan", "करण"), ("Kartik", "कार्तिक"), ("Kunal", "कुणाल"),
    ("Manish", "मनीष"), ("Mohit", "मोहित"), ("Naveen", "नवीन"), ("Nikhil", "निखिल"),
    ("Nitin", "नितिन"), ("Pankaj", "पंकज"), ("Parth", "पार्थ"), ("Piyush", "पीयूष"),
    ("Prakash", "प्रकाश"), ("Pranav", "प्रणव"), ("Praveen", "प्रवीण"), ("Rahul", "राहुल"),
    ("Rajesh", "राजेश"), ("Rakesh", "राकेश"), ("Ramesh", "रमेश"), ("Rohan", "रोहन"),
    ("Rohit", "रोहित"), ("Sachin", "सचिन"), ("Sagar", "सागर"), ("Sandeep", "संदीप"),
    ("Sanjay", "संजय"), ("Saurabh", "सौरभ"), ("Shivam", "शिवम"), ("Siddharth", "सिद्धार्थ"),
    ("Sumit", "सुमित"), ("Sunil", "सुनील"), ("Suresh", "सुरेश"), ("Tarun", "तरुण"),
    ("Varun", "वरुण"), ("Vikas", "विकास"), ("Vikram", "विक्रम"), ("Vinay", "विनय"),
    ("Vishal", "विशाल"), ("Yash", "यश"),
]

FEMALE_GIVEN = [
    ("Aarti", "आरती"), ("Aditi", "अदिति"), ("Akanksha", "आकांक्षा"), ("Alka", "अलका"),
    ("Ananya", "अनन्या"), ("Anita", "अनीता"), ("Anjali", "अंजलि"), ("Anushka", "अनुष्का"),
    ("Aparna", "अपर्णा"), ("Asha", "आशा"), ("Bhavana", "भावना"), ("Deepa", "दीपा"),
    ("Divya", "दिव्या"), ("Ekta", "एकता"), ("Gayatri", "गायत्री"), ("Geeta", "गीता"),
    ("Harini", "हरिणी"), ("Ishita", "इशिता"), ("Jyoti", "ज्योति"), ("Kavita", "कविता"),
    ("Khushi", "खुशी"), ("Kiran", "किरण"), ("Lakshmi", "लक्ष्मी"), ("Latha", "लता"),
    ("Madhuri", "माधुरी"), ("Meena", "मीना"), ("Meera", "मीरा"), ("Naina", "नैना"),
    ("Namrata", "नम्रता"), ("Neha", "नेहा"), ("Nidhi", "निधि"), ("Nisha", "निशा"),
    ("Pallavi", "पल्लवी"), ("Payal", "पायल"), ("Pooja", "पूजा"), ("Prerna", "प्रेरणा"),
    ("Priya", "प्रिया"), ("Radha", "राधा"), ("Rekha", "रेखा"), ("Riya", "रिया"),
    ("Rupa", "रूपा"), ("Sadhana", "साधना"), ("Sanjana", "संजना"), ("Saraswati", "सरस्वती"),
    ("Shreya", "श्रेया"), ("Shweta", "श्वेता"), ("Simran", "सिमरन"), ("Sneha", "स्नेहा"),
    ("Sonal", "सोनल"), ("Sunita", "सुनीता"), ("Swati", "स्वाति"), ("Tanvi", "तन्वी"),
    ("Trisha", "त्रिशा"), ("Uma", "उमा"), ("Vandana", "वंदना"), ("Varsha", "वर्षा"),
    ("Vidya", "विद्या"), ("Yamini", "यामिनी"),
]

SURNAMES = [
    ("Agarwal", "अग्रवाल"), ("Ahuja", "आहूजा"), ("Banerjee", "बनर्जी"), ("Bansal", "बंसल"),
    ("Bhat", "भट"), ("Bhattacharya", "भट्टाचार्य"), ("Bose", "बोस"), ("Chandra", "चंद्र"),
    ("Chatterjee", "चटर्जी"), ("Chauhan", "चौहान"), ("Chopra", "चोपड़ा"), ("Das", "दास"),
    ("Desai", "देसाई"), ("Deshmukh", "देशमुख"), ("Dubey", "दुबे"), ("Dutta", "दत्ता"),
    ("Gandhi", "गांधी"), ("Ghosh", "घोष"), ("Gowda", "गौड़ा"), ("Gupta", "गुप्ता"),
    ("Iyengar", "अयंगर"), ("Iyer", "अय्यर"), ("Jain", "जैन"), ("Joshi", "जोशी"),
    ("Kapoor", "कपूर"), ("Kaur", "कौर"), ("Khanna", "खन्ना"), ("Krishnan", "कृष्णन"),
    ("Kulkarni", "कुलकर्णी"), ("Kumar", "कुमार"), ("Malhotra", "मल्होत्रा"), ("Mehta", "मेहता"),
    ("Menon", "मेनन"), ("Mishra", "मिश्रा"), ("Mukherjee", "मुखर्जी"), ("Naidu", "नायडू"),
    ("Nair", "नायर"), ("Nayak", "नायक"), ("Pandey", "पांडेय"), ("Patel", "पटेल"),
    ("Patil", "पाटील"), ("Pillai", "पिल्लै"), ("Prasad", "प्रसाद"), ("Rao", "राव"),
    ("Rathore", "राठौड़"), ("Reddy", "रेड्डी"), ("Roy", "रॉय"), ("Sahu", "साहू"),
    ("Saini", "सैनी"), ("Saxena", "सक्सेना"), ("Sen", "सेन"), ("Shah", "शाह"),
    ("Sharma", "शर्मा"), ("Shetty", "शेट्टी"), ("Shukla", "शुक्ला"), ("Singh", "सिंह"),
    ("Sinha", "सिन्हा"), ("Solanki", "सोलंकी"), ("Srivastava", "श्रीवास्तव"),
    ("Subramanian", "सुब्रमण्यन"), ("Thakur", "ठाकुर"), ("Tiwari", "तिवारी"),
    ("Trivedi", "त्रिवेदी"), ("Varma", "वर्मा"), ("Venkatesan", "वेंकटेशन"), ("Verma", "वर्मा"),
    ("Yadav", "यादव"),
]

# Leading tokens used by the INITIAL_FIRST stratum.  In practice these abbreviate
# a father's name or a place name; only the initial is printed.
INITIAL_LETTERS = list("ABCDGHJKLMNPRSTVY")

# Honorifics that may be printed before the name.  Section III-B strips these
# before tokenisation; including them in the corpus exercises that code path.
HONORIFICS_M = ["Shri", "Sri", "Mr.", "Dr."]
HONORIFICS_F = ["Smt.", "Km.", "Ms.", "Dr."]

# Devanagari renderings of the abbreviated leading token used by INITIAL_FIRST.
DEVANAGARI_INITIAL = {
    "A": "ए", "B": "बी", "C": "सी", "D": "डी", "G": "जी", "H": "एच", "J": "जे",
    "K": "के", "L": "एल", "M": "एम", "N": "एन", "P": "पी", "R": "आर", "S": "एस",
    "T": "टी", "V": "वी", "Y": "वाई",
}

DEVANAGARI_HONORIFIC = {
    "Shri": "श्री", "Sri": "श्री", "Mr.": "श्री", "Dr.": "डॉ.",
    "Smt.": "श्रीमती", "Km.": "कुमारी", "Ms.": "सुश्री",
}
