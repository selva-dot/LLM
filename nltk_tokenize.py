from nltk import sent_tokenize

text = """
        Last Updated: April 6, 2007
        Exhibit 10.33
 CHASE AFFILIATE AGREEMENT
        THIS AGREEMENT sets forth the terms and conditions agreed to between Chase Bank USA, N.A. (?Chase?) and you as an “Affiliate” in the Chase
 Affiliate Program (the “Affiliate Program”). Once accepted into the Affiliate Program, an Affiliate can establish links from the Affiliate’s Website to
 [Chase.com]. Chase will pay Affiliate a fee for each approved credit card account that originates from a link in Affiliate’s Website.
 THIS IS A LEGAL AND CONTRACTUALLY BINDING AGREEMENT BETWEEN AFFILIATE AND CHASE. TO APPLY TO THE AFFILIATE
 PROGRAM, YOU MUST COMPLETE AND SUBMIT THE AFFILIATE REGISTRATION FORM AND CLICK ON THE “AGREE” BUTTON BELOW

 TO INDICATE YOUR WILLINGNESS TO BE BOUND TO CHASE BY THIS AGREEMENT. THIS AGREEMENT WILL TAKE EFFECT IF AND
 WHEN CHASE REVIEWS AND ACCEPTS YOUR REGISTRATION FORM AND PROVIDES YOU NOTICE OF ACCEPTANCE. BY SUBMITTING
 YOUR REGISTRATION FORM, AFFILIATE CERTIFIES THAT YOU HAVE READ AND UNDERSTAND THE TERMS SET FORTH BELOW, AND
 THAT YOU ARE AUTHORIZED TO SUBMIT THIS REGISTRATION FORM BY THE NAMED AFFILIATE.
 In connection with your participation in the Affiliate Program, Affiliate and Chase agree as follows:
 1. Enrollment in the Affiliate Program; Restricted Content


 To enroll in the Affiliate Program, you must submit a complete “Affiliate Registration Form” via the Chase Affiliate Website:

 For new affiliates: https://ssl.linksynergy.com/php-bin/reg/sregister.shtml?mid=2291
 For existing affiliates: http://www.linkshare.com/joinprograms?oid=87909
 Chase will evaluate your registration form and will notify you via e-mail of the acceptance or rejection of your registration form. Chase reserves, in
 its sole discretion, with or without reason, the right to accept or reject your registration into the Chase Affiliate Program, including but not limited to
 a determination that your site is unsuitable for or incompatible with the Affiliate Program based on the following criteria (collectively “Restricted
 Content”):
"""

sentences = sent_tokenize(text)

for sentence in sentences:
    print(sentence)

# """
# Last Updated: April 6, 2007
# Exhibit 10.33
# CHASE AFFILIATE AGREEMENT
# THIS AGREEMENT sets forth the terms and conditions agreed to between Chase Bank USA, N.A. (?Chase?) and you as an “Affiliate” in the Chase Affiliate Program (the “Affiliate Program”).
# Once accepted into the Affiliate Program, an Affiliate can establish links from the Affiliate’s Website to [Chase.com].
# Chase will pay Affiliate a fee for each approved credit card account that originates from a link in Affiliate’s Website.
# THIS IS A LEGAL AND CONTRACTUALLY BINDING AGREEMENT BETWEEN AFFILIATE AND CHASE.
# TO APPLY TO THE AFFILIATE PROGRAM, YOU MUST COMPLETE AND SUBMIT THE AFFILIATE REGISTRATION FORM AND CLICK ON THE “AGREE” BUTTON BELOW TO INDICATE YOUR WILLINGNESS TO BE BOUND TO CHASE BY THIS AGREEMENT.
# THIS AGREEMENT WILL TAKE EFFECT IF AND WHEN CHASE REVIEWS AND ACCEPTS YOUR REGISTRATION FORM AND PROVIDES YOU NOTICE OF ACCEPTANCE.
# BY SUBMITTING YOUR REGISTRATION FORM, AFFILIATE CERTIFIES THAT YOU HAVE READ AND UNDERSTAND THE TERMS SET FORTH BELOW, AND THAT YOU ARE AUTHORIZED TO SUBMIT THIS REGISTRATION FORM BY THE NAMED AFFILIATE.
# In connection with your participation in the Affiliate Program, Affiliate and Chase agree as follows:
# 1. Enrollment in the Affiliate Program; Restricted Content
# To enroll in the Affiliate Program, you must submit a complete “Affiliate Registration Form” via the Chase Affiliate Website:
# For new affiliates: https://ssl.linksynergy.com/php-bin/reg/sregister.shtml?mid=2291
# For existing affiliates: http://www.linkshare.com/joinprograms?oid=87909
# Chase will evaluate your registration form and will notify you via e-mail of the acceptance or rejection of your registration form.
# Chase reserves, in its sole discretion, with or without reason, the right to accept or reject your registration into the Chase Affiliate Program, including but not limited to a determination that your site is unsuitable for or incompatible with the Affiliate Program based on the following criteria (collectively “Restricted Content”):

# """


















