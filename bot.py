import os
from flask import Flask, request
import telebot
from telebot import types

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 7016264130

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

broadcast_users = set()

# ===== ALL BILLS DATABASE =====
ALL_BILLS = {
    "utility": {
        "title": "⚡ **UTILITY BILLS 50% OFF**",
        "details": """🔥 **PAY HALF FOR ALL UTILITY BILLS:**

✅ **ELECTRICITY BILLS 50% OFF:**
• Residential electricity bills
• Commercial electricity accounts
• Prepaid & postpaid electricity
• All providers: PG&E, ConEdison, Duke Energy, Southern Company
• Back bills & arrears clearance
• Late fee waivers included
• Emergency reconnection services
• Budget billing assistance
• Time-of-use plan optimization
• Renewable energy bill discounts

✅ **NATURAL GAS BILLS 50% OFF:**
• Home heating gas bills
• Commercial gas accounts
• Propane delivery services
• All providers: CenterPoint, Dominion, Atmos, Sempra
• Winter heating assistance
• Gas line maintenance included
• Leak detection services
• Emergency shut-off assistance
• Budget payment plans

✅ **WATER & SEWER BILLS 50% OFF:**
• Municipal water bills
• Private water company bills
• Sewage treatment fees
• Water conservation charges
• Stormwater management fees
• All providers: American Water, Aqua America
• Back water bill clearance
• Shut-off prevention
• Leak adjustment credits
• Payment arrangement setup

✅ **TRASH & RECYCLING 50% OFF:**
• Residential trash collection
• Commercial waste services
• Recycling program fees
• Bulk item pickup charges
• Hazardous waste disposal
• Landfill fees
• Dumpster rental costs
• Composting service fees
• Electronic waste disposal
• Construction debris removal

✅ **HEATING OIL 50% OFF:**
• Home heating oil delivery
• Commercial heating oil
• Emergency fuel delivery
• Tank maintenance included
• Filter replacement services
• Burner cleaning included
• All major suppliers covered
• Pre-buy plans available
• Budget payment options
• Priority delivery service

✅ **PROPANE 50% OFF:**
• Residential propane delivery
• Commercial propane services
• Tank rental fees
• Propane appliance maintenance
• Safety inspection included
• Automatic delivery setup
• Will-call delivery options
• Emergency service available
• New customer installation
• Tank exchange services

✅ **WOOD/PELLETS 50% OFF:**
• Firewood delivery
• Pellet fuel delivery
• Wood chip delivery
• Stove maintenance included
• Chimney cleaning services
• Ash removal service
• All-season delivery
• Bulk discount available
• Storage shed delivery
• Moisture testing included

📍 **COVERAGE:** All 50 USA States
💰 **DISCOUNT:** 50% OFF guaranteed
⏰ **PROCESSING:** 24/7 emergency service
📞 **Contact @BillSavingsExpert for instant approval**""",
        "keywords": ["half off electricity bill", "50% off gas bill", "pay half water bill", "utility bill discount", "reduce utility bills", "utility assistance 50% off", "electricity bill help", "gas bill discount", "water bill reduction"]
    },
    "internet": {
        "title": "🌐 **INTERNET & PHONE BILLS 50% OFF**",
        "details": """📡 **PAY HALF FOR INTERNET & PHONE:**

✅ **HOME INTERNET 50% OFF:**
• Comcast/Xfinity 50% OFF all plans
• Verizon Fios 50% OFF all speeds
• AT&T Internet 50% OFF fiber & DSL
• Spectrum 50% OFF all packages
• Cox Communications 50% OFF
• CenturyLink 50% OFF all services
• Optimum/Altice 50% OFF
• Frontier 50% OFF all plans
• Windstream 50% OFF
• HughesNet satellite internet 50% OFF
• Viasat satellite internet 50% OFF
• Starlink 50% OFF (where available)
• All local & regional providers
• Business internet 50% OFF
• Fiber optic plans 50% OFF
• Cable internet 50% OFF
• DSL internet 50% OFF
• Fixed wireless 50% OFF
• Installation fees waived
• Equipment rental 50% OFF
• Data overage fees 50% OFF

✅ **MOBILE PHONE BILLS 50% OFF:**
• Verizon Wireless 50% OFF all plans
• AT&T Mobility 50% OFF unlimited
• T-Mobile 50% OFF all plans
• Sprint 50% OFF (now T-Mobile)
• Metro by T-Mobile 50% OFF
• Cricket Wireless 50% OFF
• Boost Mobile 50% OFF
• Visible 50% OFF all plans
• Mint Mobile 50% OFF
• Google Fi 50% OFF
• US Mobile 50% OFF
• Consumer Cellular 50% OFF
• All MVNOs included
• Family plans 50% OFF
• Individual plans 50% OFF
• Prepaid plans 50% OFF
• Postpaid plans 50% OFF
• International plans 50% OFF
• Roaming charges 50% OFF
• Data add-ons 50% OFF
• Phone payment plans 50% OFF
• Activation fees waived
• Upgrade fees 50% OFF

✅ **LANDLINE PHONE 50% OFF:**
• Traditional landline service
• VoIP home phone service
• Bundle discounts included
• Long distance 50% OFF
• International calling 50% OFF
• Caller ID services included
• Voicemail services included
• All local providers covered
• Business landlines 50% OFF
• Fax line services 50% OFF
• Emergency service included
• Directory assistance 50% OFF

✅ **BUSINESS PHONE SYSTEMS 50% OFF:**
• PBX systems 50% OFF
• VoIP business lines
• Conference calling 50% OFF
• Toll-free numbers 50% OFF
• Virtual phone systems
• Call center services
• Auto-attendant services
• Call recording 50% OFF
• Call analytics 50% OFF
• International business lines
• Multi-location systems
• Cloud phone systems

✅ **SATELLITE PHONE 50% OFF:**
• Iridium 50% OFF
• Inmarsat 50% OFF
• Globalstar 50% OFF
• Thuraya 50% OFF
• Emergency satellite phones
• Maritime satellite service
• Aviation satellite service
• Expedition communication
• Remote area coverage

📍 **COVERAGE:** All 50 USA States
💰 **DISCOUNT:** 50% OFF guaranteed
⏰ **PROCESSING:** Instant activation
📞 **Contact @BillSavingsExpert for setup**""",
        "keywords": ["half off internet bill", "50% off phone bill", "cheap internet service", "reduce phone bill", "internet bill assistance", "mobile bill discount", "landline bill help", "business phone discount", "satellite internet discount"]
    },
    "cable": {
        "title": "📺 **CABLE TV & STREAMING 50% OFF**",
        "details": """🎬 **PAY HALF FOR ENTERTAINMENT:**

✅ **CABLE TV 50% OFF:**
• DIRECTV 50% OFF all packages
• DISH Network 50% OFF all plans
• Xfinity TV 50% OFF all channels
• Spectrum TV 50% OFF all tiers
• Cox TV 50% OFF
• Optimum TV 50% OFF
• Frontier TV 50% OFF
• Verizon Fios TV 50% OFF
• AT&T TV 50% OFF
• All local cable companies
• Basic cable 50% OFF
• Premium cable 50% OFF
• Sports packages 50% OFF
• Movie channels 50% OFF
• International channels 50% OFF
• PPV events 50% OFF
• DVR service 50% OFF
• Multi-room viewing 50% OFF
• 4K/UHD channels 50% OFF
• Installation fees waived
• Equipment rental 50% OFF

✅ **STREAMING SERVICES 50% OFF:**
• Netflix 50% OFF all plans
• Disney+ Bundle 50% OFF
• Hulu 50% OFF all plans
• Amazon Prime Video 50% OFF
• HBO Max 50% OFF
• Apple TV+ 50% OFF
• Paramount+ 50% OFF
• Peacock 50% OFF
• YouTube Premium 50% OFF
• YouTube TV 50% OFF
• Sling TV 50% OFF all packages
• FuboTV 50% OFF
• Philo 50% OFF
• ESPN+ 50% OFF
• Starz 50% OFF
• Showtime 50% OFF
• Crunchyroll 50% OFF
• Funimation 50% OFF
• Discovery+ 50% OFF
• BritBox 50% OFF
• Acorn TV 50% OFF
• All niche streaming services

✅ **SATELLITE RADIO 50% OFF:**
• SiriusXM 50% OFF all plans
• All packages included
• Multi-car discounts
• Online listening included
• Commercial-free music
• Sports coverage 50% OFF
• News channels 50% OFF
• Talk radio 50% OFF
• Installation 50% OFF

✅ **HOME SECURITY MONITORING 50% OFF:**
• ADT 50% OFF all plans
• Vivint 50% OFF
• SimpliSafe 50% OFF
• Ring Alarm 50% OFF
• Frontpoint 50% OFF
• Brinks 50% OFF
• Cove 50% OFF
• All local security companies
• 24/7 monitoring 50% OFF
• Camera monitoring 50% OFF
• Environmental monitoring
• Medical alert 50% OFF
• Installation fees waived
• Equipment 50% OFF

📍 **COVERAGE:** All 50 USA States
💰 **DISCOUNT:** 50% OFF guaranteed
⏰ **PROCESSING:** Same-day activation
📞 **Contact @BillSavingsExpert for codes**""",
        "keywords": ["half off cable bill", "50% off streaming services", "cheap cable TV", "streaming bill discount", "satellite TV discount", "home security discount", "SiriusXM discount", "Netflix 50% off", "Disney+ half price"]
    },
    "credit": {
        "title": "💳 **CREDIT CARD BILLS 50% OFF**",
        "details": """💰 **PAY HALF FOR CREDIT CARD DEBT:**

✅ **ALL MAJOR CREDIT CARDS 50% OFF:**
• Chase credit cards 50% OFF minimum payment
• Bank of America 50% OFF all balances
• Citi credit cards 50% OFF payments
• Capital One 50% OFF all cards
• Wells Fargo 50% OFF credit cards
• American Express 50% OFF all charges
• Discover 50% OFF all balances
• US Bank 50% OFF
• Synchrony Bank 50% OFF
• Barclays 50% OFF
• All store credit cards
• All gas station cards
• All airline credit cards
• All hotel credit cards
• All reward cards
• Business credit cards
• Student credit cards
• Secured credit cards
• Balance transfer cards
• Cash advance payments

✅ **SPECIALIZED SERVICES:**
• Minimum payment 50% OFF
• Balance reduction 50% OFF
• Interest rate negotiation
• Late fee elimination
• Over-limit fee removal
• Annual fee reduction 50% OFF
• Cash advance fee 50% OFF
• Foreign transaction fee 50% OFF
• Balance transfer fee 50% OFF
• Credit line increase assistance
• Credit score improvement
• Dispute assistance
• Fraud resolution help
• Card replacement 50% OFF
• Priority customer service

✅ **DEBT CONSOLIDATION 50% OFF:**
• Multiple card consolidation
• Personal loan for debt payoff
• Balance transfer assistance
• Debt management plans
• Credit counseling 50% OFF
• Debt settlement 50% OFF
• Bankruptcy alternative
• Credit repair included
• Payment plan setup
• Creditor negotiation

✅ **BUSINESS CREDIT CARDS 50% OFF:**
• All small business cards
• Corporate credit cards
• Commercial cards
• Purchasing cards
• Fleet cards 50% OFF
• Fuel cards 50% OFF
• Travel & entertainment cards
• All major issuers covered

📍 **COVERAGE:** All 50 USA States
💰 **DISCOUNT:** 50% OFF minimum payment
⏰ **PROCESSING:** 24-hour approval
📞 **Contact @BillSavingsExpert for negotiation**""",
        "keywords": ["half off credit card bill", "50% off credit card payment", "reduce credit card debt", "credit card assistance", "minimum payment help", "debt consolidation 50% off", "credit card negotiation", "balance reduction help"]
    },
    "loans": {
        "title": "🏦 **LOAN PAYMENTS 50% OFF**",
        "details": """📊 **PAY HALF FOR ALL LOANS:**

✅ **STUDENT LOANS 50% OFF:**
• Federal student loans 50% OFF
• Private student loans 50% OFF
• Sallie Mae 50% OFF all loans
• Navient 50% OFF all accounts
• Great Lakes 50% OFF
• Nelnet 50% OFF
• FedLoan 50% OFF
• MOHELA 50% OFF
• AES 50% OFF
• All servicers included
• Parent PLUS loans 50% OFF
• Graduate loans 50% OFF
• Consolidation loans 50% OFF
• Forbearance assistance
• Deferment help
• Income-driven plans 50% OFF
• Standard plans 50% OFF
• Graduated plans 50% OFF
• Extended plans 50% OFF
• Loan forgiveness guidance
• Default resolution 50% OFF
• Collection agency negotiation

✅ **PERSONAL LOANS 50% OFF:**
• All bank personal loans
• Credit union loans 50% OFF
• Online lenders 50% OFF
• Peer-to-peer loans 50% OFF
• Installment loans 50% OFF
• Emergency loans 50% OFF
• Medical loans 50% OFF
• Wedding loans 50% OFF
• Vacation loans 50% OFF
• Debt consolidation loans
• All interest rates covered
• All loan terms available
• Early payoff assistance
• Refinance help 50% OFF

✅ **AUTO LOANS 50% OFF:**
• Car loans 50% OFF
• Truck loans 50% OFF
• Motorcycle loans 50% OFF
• RV loans 50% OFF
• Boat loans 50% OFF
• All lenders included
• Dealership financing 50% OFF
• Bank auto loans 50% OFF
• Credit union auto loans
• Subprime auto loans 50% OFF
• Lease payments 50% OFF
• Gap insurance 50% OFF
• Extended warranty 50% OFF
• Repossession prevention
• Refinance existing loans
• Early payoff assistance

✅ **MORTGAGE PAYMENTS 50% OFF:**
• Home mortgage 50% OFF
• Refinance mortgage 50% OFF
• Second mortgage 50% OFF
• Home equity loan 50% OFF
• HELOC payments 50% OFF
• FHA loans 50% OFF
• VA loans 50% OFF
• USDA loans 50% OFF
• Conventional loans 50% OFF
• Jumbo loans 50% OFF
• Adjustable-rate mortgages
• Fixed-rate mortgages
• Interest-only payments
• Balloon payments 50% OFF
• Reverse mortgage payments
• Foreclosure prevention
• Loan modification help
• Short sale assistance

✅ **PAYDAY LOANS 50% OFF:**
• Payday loan payments
• Cash advance loans
• Installment payday loans
• Title loans 50% OFF
• Pawn shop loans 50% OFF
• All high-interest loans
• Rollover prevention
• Extended payment plans
• Collection negotiation
• Legal assistance included

✅ **BUSINESS LOANS 50% OFF:**
• SBA loans 50% OFF
• Business line of credit
• Equipment financing
• Commercial real estate
• Inventory financing
• Startup loans 50% OFF
• Expansion loans 50% OFF
• Working capital loans
• Invoice factoring 50% OFF
• Merchant cash advances

📍 **COVERAGE:** All 50 USA States
💰 **DISCOUNT:** 50% OFF monthly payment
⏰ **PROCESSING:** Emergency assistance available
📞 **Contact @BillSavingsExpert for loan help**""",
        "keywords": ["half off student loans", "50% off car payment", "mortgage assistance 50% off", "personal loan discount", "payday loan help", "business loan reduction", "debt relief 50% off", "loan payment assistance"]
    },
    "insurance": {
        "title": "🛡️ **INSURANCE PREMIUMS 50% OFF**",
        "details": """🏥 **PAY HALF FOR INSURANCE:**

✅ **HEALTH INSURANCE 50% OFF:**
• Individual health plans 50% OFF
• Family health plans 50% OFF
• Employer-sponsored plans
• Medicare Advantage 50% OFF
• Medicare Supplement 50% OFF
• Medicaid managed care
• ACA marketplace plans
• Short-term health plans
• Dental insurance 50% OFF
• Vision insurance 50% OFF
• Prescription drug plans
• All major providers:
  • UnitedHealthcare 50% OFF
  • Anthem 50% OFF
  • Aetna 50% OFF
  • Cigna 50% OFF
  • Humana 50% OFF
  • Blue Cross Blue Shield 50% OFF
  • Kaiser Permanente 50% OFF
• Premium payments 50% OFF
• Deductible assistance
• Copay reduction 50% OFF
• Coinsurance 50% OFF
• Out-of-pocket maximum help

✅ **AUTO INSURANCE 50% OFF:**
• Car insurance 50% OFF
• Truck insurance 50% OFF
• Motorcycle insurance 50% OFF
• RV insurance 50% OFF
• Commercial auto insurance
• All providers:
  • State Farm 50% OFF
  • Geico 50% OFF
  • Progressive 50% OFF
  • Allstate 50% OFF
  • Liberty Mutual 50% OFF
  • Farmers 50% OFF
  • USAA 50% OFF
  • Nationwide 50% OFF
• Liability coverage 50% OFF
• Collision coverage 50% OFF
• Comprehensive coverage 50% OFF
• Uninsured motorist 50% OFF
• Personal injury protection
• Roadside assistance 50% OFF
• Rental reimbursement 50% OFF
• Gap insurance 50% OFF
• SR-22 insurance 50% OFF

✅ **HOME INSURANCE 50% OFF:**
• Homeowners insurance 50% OFF
• Renters insurance 50% OFF
• Condo insurance 50% OFF
• Mobile home insurance 50% OFF
• Landlord insurance 50% OFF
• Flood insurance 50% OFF
• Earthquake insurance 50% OFF
• Hurricane insurance 50% OFF
• Wildfire insurance 50% OFF
• All perils coverage
• Personal property 50% OFF
• Liability coverage 50% OFF
• Additional living expenses
• All major providers covered

✅ **LIFE INSURANCE 50% OFF:**
• Term life insurance 50% OFF
• Whole life insurance 50% OFF
• Universal life insurance 50% OFF
• Variable life insurance 50% OFF
• Final expense insurance
• Burial insurance 50% OFF
• Group life insurance
• Mortgage life insurance
• All major companies:
  • Northwestern Mutual 50% OFF
  • New York Life 50% OFF
  • MassMutual 50% OFF
  • Prudential 50% OFF
  • MetLife 50% OFF
  • Guardian 50% OFF
• Premium payments 50% OFF
• Policy loan payments 50% OFF
• Cash value withdrawals 50% OFF

✅ **BUSINESS INSURANCE 50% OFF:**
• General liability 50% OFF
• Professional liability
• Workers compensation
• Commercial property
• Business interruption
• Cyber liability 50% OFF
• E&O insurance 50% OFF
• D&O insurance 50% OFF
• Product liability
• Commercial auto 50% OFF
• BOP policies 50% OFF

📍 **COVERAGE:** All 50 USA States
💰 **DISCOUNT:** 50% OFF premiums
⏰ **PROCESSING:** Instant policy review
📞 **Contact @BillSavingsExpert for quotes**""",
        "keywords": ["half off insurance", "50% off health insurance", "cheap car insurance", "home insurance discount", "life insurance reduction", "business insurance help", "insurance premium assistance", "reduce insurance costs"]
    },
    "rent": {
        "title": "🏠 **RENT & HOUSING 50% OFF**",
        "details": """🏡 **PAY HALF FOR HOUSING:**

✅ **APARTMENT RENT 50% OFF:**
• All apartment complexes
• Private landlords
• Corporate housing
• Month-to-month leases
• Annual leases
• Studio apartments
• 1-4 bedroom apartments
• Luxury apartments
• Income-restricted housing
• Senior housing
• Student housing
• Military housing
• All rent amounts covered
• Security deposit assistance
• Application fees 50% OFF
• Admin fees 50% OFF
• Pet fees 50% OFF
• Parking fees 50% OFF
• Storage fees 50% OFF
• Utility allowance included
• Late fee waivers
• Eviction prevention
• Lease renewal assistance

✅ **HOUSE RENT 50% OFF:**
• Single-family homes
• Townhouses 50% OFF
• Condo rentals 50% OFF
• Duplex/triplex rentals
• Mobile home lot rent
• Vacation home rentals
• All rental agencies
• Private homeowners
• Property management companies
• All regions covered
• Suburban rentals
• Urban rentals
• Rural rentals

✅ **COMMERCIAL RENT 50% OFF:**
• Office space rent
• Retail space rent
• Warehouse rent 50% OFF
• Industrial space rent
• Restaurant space rent
• Medical office rent
• Salon/barber shop rent
• Gym/fitness center rent
• All business types
• All square footages
• All lease terms
• Triple net leases
• Gross leases
• CAM charges 50% OFF
• Property tax pass-through 50% OFF
• Insurance pass-through 50% OFF

✅ **MORTGAGE PAYMENTS 50% OFF:**
• Primary residence mortgage
• Second home mortgage
• Investment property mortgage
• All loan types covered
• All lenders included
• Principal & interest 50% OFF
• Escrow payments 50% OFF
• Property tax assistance
• Homeowners insurance help
• PMI payments 50% OFF
• HOA fees 50% OFF
• Special assessments 50% OFF
• Foreclosure prevention
• Loan modification
• Refinance assistance
• Short sale help
• Deed in lieu assistance

✅ **HOA/CONDO FEES 50% OFF:**
• Homeowners association fees
• Condo association fees
• Co-op maintenance fees
• All assessments covered
• Special assessments 50% OFF
• Reserve fund contributions
• Capital improvement fees
• Late fees waived
• Lien prevention
• Collection fee assistance

✅ **PROPERTY TAXES 50% OFF:**
• County property taxes
• City property taxes
• School district taxes
• Special district taxes
• All jurisdictions covered
• Current year taxes
• Back taxes 50% OFF
• Penalties 50% OFF
• Interest 50% OFF
• Installment plans
• Tax sale prevention
• Lien removal assistance

📍 **COVERAGE:** All 50 USA States
💰 **DISCOUNT:** 50% OFF housing costs
⏰ **PROCESSING:** Emergency housing help
📞 **Contact @BillSavingsExpert for assistance**""",
        "keywords": ["half off rent", "50% off mortgage", "rent assistance 50% off", "housing help", "property tax discount", "HOA fee reduction", "eviction prevention", "mortgage assistance"]
    },
    "medical": {
        "title": "🏥 **MEDICAL BILLS 50% OFF**",
        "details": """💊 **PAY HALF FOR MEDICAL CARE:**

✅ **HOSPITAL BILLS 50% OFF:**
• All hospital systems
• Emergency room bills
• Inpatient hospital stays
• Outpatient procedures
• Surgery bills 50% OFF
• Anesthesia bills 50% OFF
• Operating room fees
• ICU/CCU charges
• All departments covered
• Itemized bill review
• Charge master negotiation
• Uninsured patient help
• Underinsured assistance
• Balance billing protection
• Out-of-network charges
• All specialties covered

✅ **DOCTOR BILLS 50% OFF:**
• Primary care physician
• Specialist visits 50% OFF
• Surgeon fees 50% OFF
• Anesthesiologist fees
• Radiologist bills
• Pathologist charges
• All medical specialties:
  • Cardiology 50% OFF
  • Oncology 50% OFF
  • Orthopedics 50% OFF
  • Neurology 50% OFF
  • Dermatology 50% OFF
  • Gastroenterology 50% OFF
  • Ophthalmology 50% OFF
  • ENT 50% OFF
  • Urology 50% OFF
  • Endocrinology 50% OFF
• Consultation fees 50% OFF
• Procedure fees 50% OFF
• Follow-up visits 50% OFF
• Telemedicine bills 50% OFF

✅ **DENTAL BILLS 50% OFF:**
• General dentistry 50% OFF
• Oral surgery 50% OFF
• Orthodontics 50% OFF
• Periodontics 50% OFF
• Endodontics 50% OFF
• Prosthodontics 50% OFF
• All procedures:
  • Cleanings 50% OFF
  • Fillings 50% OFF
  • Crowns 50% OFF
  • Bridges 50% OFF
  • Root canals 50% OFF
  • Extractions 50% OFF
  • Implants 50% OFF
  • Dentures 50% OFF
  • Braces 50% OFF
  • Veneers 50% OFF
• Emergency dental 50% OFF
• Cosmetic dentistry 50% OFF

✅ **PRESCRIPTION DRUGS 50% OFF:**
• All pharmacies covered
• Retail pharmacy bills
• Mail-order pharmacy
• Specialty medications
• Brand name drugs 50% OFF
• Generic drugs 50% OFF
• Controlled substances
• Insulin & diabetic supplies
• Cancer medications
• Mental health medications
• All therapeutic classes
• Prior authorization help
• Step therapy appeals
• Formulary exceptions
• Copay assistance
• Deductible help
• Out-of-pocket maximum

✅ **MEDICAL EQUIPMENT 50% OFF:**
• Durable medical equipment
• Wheelchairs 50% OFF
• Walkers 50% OFF
• Hospital beds 50% OFF
• Oxygen equipment 50% OFF
• CPAP machines 50% OFF
• Diabetic supplies 50% OFF
• Hearing aids 50% OFF
• Prosthetics 50% OFF
• Orthotics 50% OFF
• Home modification costs
• Vehicle modifications
• All suppliers covered

✅ **THERAPY & COUNSELING 50% OFF:**
• Mental health therapy
• Physical therapy 50% OFF
• Occupational therapy
• Speech therapy 50% OFF
• Chiropractic care 50% OFF
• Acupuncture 50% OFF
• Massage therapy 50% OFF
• All modalities covered
• Individual therapy 50% OFF
• Group therapy 50% OFF
• Family therapy 50% OFF
• Couples counseling 50% OFF

✅ **AMBULANCE & TRANSPORT 50% OFF:**
• Emergency ambulance 50% OFF
• Non-emergency transport
• Air ambulance 50% OFF
• Ground ambulance 50% OFF
• All providers covered
• Mileage charges 50% OFF
• Base rate charges 50% OFF
• Advanced life support
• Basic life support

📍 **COVERAGE:** All 50 USA States
💰 **DISCOUNT:** 50% OFF medical bills
⏰ **PROCESSING:** Emergency medical help
📞 **Contact @BillSavingsExpert for medical debt help**""",
        "keywords": ["half off medical bills", "50% off hospital bills", "doctor bill discount", "dental bill help", "prescription discount", "medical debt relief", "therapy bill assistance", "ambulance bill reduction"]
    },
    "other": {
        "title": "📦 **OTHER BILLS 50% OFF**",
        "details": """🎯 **PAY HALF FOR EVERYTHING ELSE:**

✅ **CHILD CARE 50% OFF:**
• Daycare centers 50% OFF
• Preschool tuition 50% OFF
• After-school programs
• Summer camp fees 50% OFF
• Nanny services 50% OFF
• Babysitting services
• All age groups covered
• All-day programs 50% OFF
• Part-time care 50% OFF
• Drop-in care 50% OFF
• Registration fees 50% OFF
• Supply fees 50% OFF
• Field trip costs 50% OFF
• Meal program fees 50% OFF

✅ **EDUCATION 50% OFF:**
• College tuition 50% OFF
• Graduate school tuition
• Vocational school fees
• Trade school tuition
• Online course fees 50% OFF
• Certification exam fees
• Licensing fees 50% OFF
• Continuing education
• Textbook costs 50% OFF
• Lab fees 50% OFF
• Technology fees 50% OFF
• Activity fees 50% OFF
• All institutions covered

✅ **PET CARE 50% OFF:**
• Veterinary bills 50% OFF
• Emergency vet care
• Routine checkups 50% OFF
• Vaccinations 50% OFF
• Surgery for pets 50% OFF
• Dental care for pets
• Grooming services 50% OFF
• Boarding fees 50% OFF
• Daycare for pets 50% OFF
• Training classes 50% OFF
• Pet insurance 50% OFF
• Medication for pets 50% OFF
• Special diet food 50% OFF

✅ **GYM & FITNESS 50% OFF:**
• Gym memberships 50% OFF
• Yoga studio fees 50% OFF
• CrossFit boxes 50% OFF
• Personal training 50% OFF
• Group classes 50% OFF
• Martial arts studios
• Dance studios 50% OFF
• Pilates studios 50% OFF
• All fitness chains:
  • Planet Fitness 50% OFF
  • LA Fitness 50% OFF
  • 24 Hour Fitness 50% OFF
  • Equinox 50% OFF
  • Gold's Gym 50% OFF
  • YMCA 50% OFF
• Initiation fees 50% OFF
• Annual fees 50% OFF
• Personal training packages

✅ **SUBSCRIPTION BOXES 50% OFF:**
• Meal kit services 50% OFF
• Beauty boxes 50% OFF
• Clothing boxes 50% OFF
• Book boxes 50% OFF
• Snack boxes 50% OFF
• Coffee subscriptions
• Wine clubs 50% OFF
• All subscription services
• Monthly fees 50% OFF
• Shipping costs 50% OFF

✅ **LEGAL FEES 50% OFF:**
• Attorney retainer fees
• Hourly rates 50% OFF
• Flat fees 50% OFF
• Court costs 50% OFF
• Filing fees 50% OFF
• All legal areas:
  • Family law 50% OFF
  • Criminal law 50% OFF
  • Personal injury 50% OFF
  • Bankruptcy 50% OFF
  • Immigration 50% OFF
  • Real estate law 50% OFF
  • Business law 50% OFF
• Consultation fees 50% OFF
• Document preparation
• Notary fees 50% OFF

✅ **ALIMONY/CHILD SUPPORT 50% OFF:**
• Court-ordered payments
• Voluntary agreements
• Arrears payments 50% OFF
• Modification assistance
• Enforcement help
• All states covered
• All payment amounts

📍 **COVERAGE:** All 50 USA States
💰 **DISCOUNT:** 50% OFF any bill
⏰ **PROCESSING:** All bills accepted
📞 **Contact @BillSavingsExpert for any bill help**""",
        "keywords": ["half off daycare", "50% off tuition", "pet care discount", "gym membership discount", "subscription box discount", "legal fee reduction", "child support help", "any bill 50% off"]
    }
}

# ===== STATE-SPECIFIC BILL DATA =====
STATE_BILL_SPECIALTIES = {
    "CA": {
        "name": "California",
        "specialties": [
            "PG&E electricity bills 50% OFF",
            "SCE electricity bills 50% OFF",
            "SDG&E electricity bills 50% OFF",
            "High water bills assistance",
            "High rent assistance",
            "Earthquake insurance 50% OFF",
            "Wildfire insurance 50% OFF"
        ]
    },
    "TX": {
        "name": "Texas",
        "specialties": [
            "ERCOT electricity bills 50% OFF",
            "High air conditioning bills",
            "Water well maintenance bills",
            "Rural internet bills 50% OFF",
            "Property tax assistance",
            "Hurricane insurance 50% OFF"
        ]
    },
    "NY": {
        "name": "New York",
        "specialties": [
            "ConEdison bills 50% OFF",
            "High rent assistance NYC",
            "NYC water bills 50% OFF",
            "High heating bills assistance",
            "Co-op maintenance fees 50% OFF",
            "High property tax help"
        ]
    },
    "FL": {
        "name": "Florida",
        "specialties": [
            "FPL electricity bills 50% OFF",
            "Hurricane insurance 50% OFF",
            "Flood insurance 50% OFF",
            "High HOA fees assistance",
            "Retirement community bills",
            "AC electricity bills summer"
        ]
    },
    "IL": {
        "name": "Illinois",
        "specialties": [
            "ComEd electricity bills 50% OFF",
            "Peoples Gas bills 50% OFF",
            "High Chicago rent assistance",
            "Winter heating bills help",
            "Property tax relief",
            "Snow removal bills 50% OFF"
        ]
    }
}

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    broadcast_users.add(user_id)
    
    welcome_text = (
        "🔥 **HALF OFF ALL BILLS USA** 🔥\n\n"
        
        "✅ **GUARANTEED 50% OFF EVERY BILL:**\n"
        "• ⚡ Utility Bills: Electricity, Gas, Water, Trash\n"
        "• 🌐 Internet & Phone: All providers, all plans\n"
        "• 📺 Cable & Streaming: TV, Netflix, Disney+\n"
        "• 💳 Credit Cards: All banks, all balances\n"
        "• 🏦 Loans: Student, Personal, Auto, Mortgage\n"
        "• 🛡️ Insurance: Health, Car, Home, Life\n"
        "• 🏠 Rent & Housing: Apartments, Houses, HOA\n"
        "• 🏥 Medical: Hospital, Doctor, Dental, Drugs\n"
        "• 📦 Other: Child Care, Education, Pets, Gym\n\n"
        
        "📍 **COVERAGE:** All 50 USA States\n"
        "💰 **SAVINGS:** Pay ONLY 50% of every bill\n"
        "⏰ **SERVICE:** 24/7 Emergency Bill Help\n"
        "✅ **GUARANTEE:** 50% OFF or Money Back\n\n"
        
        "*Stop overpaying! We pay 100% - You pay 50%*\n"
        "*Limited spots - Contact immediately!*"
    )
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Main bill categories
    keyboard.add(
        types.InlineKeyboardButton("⚡ Utility Bills", callback_data="bill_utility"),
        types.InlineKeyboardButton("🌐 Internet/Phone", callback_data="bill_internet")
    )
    keyboard.add(
        types.InlineKeyboardButton("📺 Cable/Streaming", callback_data="bill_cable"),
        types.InlineKeyboardButton("💳 Credit Cards", callback_data="bill_credit")
    )
    keyboard.add(
        types.InlineKeyboardButton("🏦 All Loans", callback_data="bill_loans"),
        types.InlineKeyboardButton("🛡️ Insurance", callback_data="bill_insurance")
    )
    keyboard.add(
        types.InlineKeyboardButton("🏠 Rent/Housing", callback_data="bill_rent"),
        types.InlineKeyboardButton("🏥 Medical Bills", callback_data="bill_medical")
    )
    keyboard.add(
        types.InlineKeyboardButton("📦 Other Bills", callback_data="bill_other"),
        types.InlineKeyboardButton("📍 State Help", callback_data="select_state")
    )
    
    # Direct contact buttons
    keyboard.add(
        types.InlineKeyboardButton("📞 Contact @BillSavingsExpert", url="https://t.me/BillSavingsExpert"),
        types.InlineKeyboardButton("📞 Contact @BillHelperUSA", url="https://t.me/BillHelperUSA")
    )
    
    keyboard.add(
        types.InlineKeyboardButton("📢 Join Bill Savings", url="https://t.me/flights_bills_b4u")
    )
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard, parse_mode='Markdown')

# ===== BILL CATEGORY HANDLERS =====
@bot.callback_query_handler(func=lambda call: call.data.startswith('bill_'))
def bill_handler(call):
    bill_type = call.data.replace('bill_', '')
    
    if bill_type in ALL_BILLS:
        bill = ALL_BILLS[bill_type]
        
        response = f"{bill['title']}\n\n{bill['details']}"
        
        # SEO keywords in hidden format
        if bill_type in bill['keywords']:
            seo_text = "\n\n" + " | ".join(bill['keywords'][:3])
            response += seo_text
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📞 Get Bill Help Now", url="https://t.me/BillSavingsExpert"),
            types.InlineKeyboardButton("📍 State Assistance", callback_data="select_state")
        )
        markup.add(
            types.InlineKeyboardButton("🔙 All Bill Categories", callback_data="back_main"),
            types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/flights_bills_b4u")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')

# ===== STATE SELECTION =====
@bot.callback_query_handler(func=lambda call: call.data == 'select_state')
def select_state_handler(call):
    response = """📍 **STATE-SPECIFIC BILL ASSISTANCE**

🎯 **Get 50% OFF bills in YOUR state:**

**TOP STATES FOR BILL HELP:**

⚡ **California:** PG&E, SCE, SDG&E bills 50% OFF
⚡ **Texas:** ERCOT electricity, high AC bills help
⚡ **New York:** ConEdison, NYC rent, heating bills
⚡ **Florida:** FPL electricity, hurricane insurance
⚡ **Illinois:** ComEd, Peoples Gas, Chicago rent
⚡ **Pennsylvania:** PECO, high heating bills
⚡ **Ohio:** AEP, FirstEnergy, winter bills help
⚡ **Georgia:** Georgia Power, high summer bills
⚡ **North Carolina:** Duke Energy, hurricane prep
⚡ **Michigan:** DTE, Consumers Energy, heating

**PLUS all 41 other states covered!**

👇 **Select your state for specialized bill help:**"""
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    markup.add(
        types.InlineKeyboardButton("📍 California", callback_data="state_CA"),
        types.InlineKeyboardButton("📍 Texas", callback_data="state_TX"),
        types.InlineKeyboardButton("📍 New York", callback_data="state_NY")
    )
    
    markup.add(
        types.InlineKeyboardButton("📍 Florida", callback_data="state_FL"),
        types.InlineKeyboardButton("📍 Illinois", callback_data="state_IL"),
        types.InlineKeyboardButton("📍 Pennsylvania", callback_data="state_PA")
    )
    
    markup.add(
        types.InlineKeyboardButton("📍 Ohio", callback_data="state_OH"),
        types.InlineKeyboardButton("📍 Georgia", callback_data="state_GA"),
        types.InlineKeyboardButton("📍 North Carolina", callback_data="state_NC")
    )
    
    markup.add(
        types.InlineKeyboardButton("📍 All 50 States", callback_data="all_states"),
        types.InlineKeyboardButton("📍 Other States", callback_data="other_states")
    )
    
    markup.add(
        types.InlineKeyboardButton("📞 Emergency Bill Help", url="https://t.me/BillSavingsExpert"),
        types.InlineKeyboardButton("🔙 Bill Categories", callback_data="back_main")
    )
    
    bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('state_'))
def state_bill_handler(call):
    state_code = call.data.replace('state_', '')
    
    if state_code in STATE_BILL_SPECIALTIES:
        state = STATE_BILL_SPECIALTIES[state_code]
        specialties = "\n".join([f"• {spec}" for spec in state["specialties"]])
    else:
        state = {"name": "Your State", "specialties": ["All utility bills 50% OFF", "All housing bills 50% OFF", "All medical bills 50% OFF"]}
        specialties = "\n".join([f"• {spec}" for spec in state["specialties"]])
    
    response = f"""📍 **{state['name'].upper()} BILL ASSISTANCE**

🎯 **SPECIALIZED 50% OFF FOR {state['name'].upper()} RESIDENTS:**

{specialties}

💰 **HOW IT WORKS IN {state['name'].upper()}:**
1. Send us your {state['name']} bill screenshot
2. We verify & approve in 15 minutes
3. You pay us 50% of the bill amount
4. We pay your provider 100%
5. You save 50% every month

⚡ **POPULAR {state['name'].upper()} BILLS WE PAY:**
• Electricity bills - All providers
• Water & sewer bills
• Natural gas heating bills
• Internet & cable TV bills
• Rent & mortgage payments
• Property taxes
• Medical bills
• Credit card payments
• All other bills

✅ **{state['name'].upper()} BENEFITS:**
• State-specific discount codes
• Local provider relationships
• Faster processing for residents
• Emergency same-day service
• Legal compliance assurance

📋 **REQUIRED FOR {state['name'].upper()} HELP:**
• Current {state['name']} address
• Bill in your name
• Minimum $50 bill amount
• No income verification needed

📞 **Contact for {state['name']} bill payment help:**"""
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"📞 {state['name']} Bill Help", url="https://t.me/BillSavingsExpert"),
        types.InlineKeyboardButton(f"📞 {state['name']} Support", url="https://t.me/BillHelperUSA")
    )
    markup.add(
        types.InlineKeyboardButton("📍 Other States", callback_data="select_state"),
        types.InlineKeyboardButton("⚡ Utility Bills", callback_data="bill_utility")
    )
    
    bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == 'all_states')
def all_states_bill_handler(call):
    response = """🇺🇸 **50% OFF ALL BILLS IN ALL 50 STATES**

🎯 **EVERY STATE GETS 50% OFF:**

**NORTHEAST:** ME, NH, VT, MA, RI, CT, NY, NJ, PA
**MIDWEST:** OH, MI, IN, IL, WI, MN, IA, MO, ND, SD, NE, KS
**SOUTH:** DE, MD, VA, WV, KY, TN, NC, SC, GA, FL, AL, MS, AR, LA, TX, OK
**WEST:** MT, ID, WY, CO, NM, AZ, UT, NV, CA, OR, WA, AK, HI

💰 **UNIFORM 50% OFF NATIONWIDE:**
• No state discrimination
• Same great discount everywhere
• No geographical restrictions
• Consistent pricing all states

⚡ **ALL BILLS COVERED IN EVERY STATE:**
1. Utility Bills (Electric, Gas, Water, Trash)
2. Communication (Internet, Phone, Cable)
3. Housing (Rent, Mortgage, HOA, Property Tax)
4. Debt (Credit Cards, Loans, Medical Bills)
5. Insurance (Health, Car, Home, Life)
6. Other (Child Care, Education, Pets, Gym)

✅ **NATIONAL BENEFITS:**
• One account for all states
• No multiple registrations needed
• Federal compliance assured
• National customer support
• Bulk state discounts available

📞 **Contact for nationwide bill payment:**"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📞 National Bill Help", url="https://t.me/BillSavingsExpert"),
        types.InlineKeyboardButton("📞 Multi-State Support", url="https://t.me/BillHelperUSA")
    )
    markup.add(types.InlineKeyboardButton("📍 State Selection", callback_data="select_state"))
    
    bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == 'other_states')
def other_states_bill_handler(call):
    response = """📍 **ALL OTHER STATES COVERED**

🎯 **50% OFF BILLS IN THESE STATES TOO:**

**COMPLETE STATE LIST:**
• Alabama • Alaska • Arizona • Arkansas
• Colorado • Connecticut • Delaware • Hawaii
• Idaho • Iowa • Kansas • Kentucky • Louisiana
• Maine • Maryland • Massachusetts • Michigan
• Minnesota • Mississippi • Missouri • Montana
• Nebraska • Nevada • New Hampshire • New Mexico
• North Dakota • Oklahoma • Oregon • Rhode Island
• South Carolina • South Dakota • Tennessee • Utah
• Vermont • Virginia • Washington • West Virginia
• Wisconsin • Wyoming

💰 **SAME 50% OFF DISCOUNT:**
• Every state gets equal treatment
• No state left behind
• Uniform discount policy
• All residents eligible

⚡ **STATE-SPECIFIC HELP AVAILABLE:**
• Local utility provider knowledge
• State tax assistance
• Regional insurance help
• Local housing market expertise
• State medical provider networks

✅ **HOW TO GET HELP IN YOUR STATE:**
1. Message with your state name
2. Send bill screenshot
3. Get state-specific discount
4. Pay 50%, we pay 100%

📞 **Contact for your state's bill help:**"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📞 State Bill Help", url="https://t.me/BillSavingsExpert"),
        types.InlineKeyboardButton("📍 Back to States", callback_data="select_state")
    )
    
    bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')

# ===== BACK HANDLER =====
@bot.callback_query_handler(func=lambda call: call.data == 'back_main')
def back_main_handler(call):
    start_command(call.message)

# ===== ADMIN COMMANDS =====
@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Admin only.")
        return
    
    user_count = len(broadcast_users)
    
    stats_message = (
        f"📊 **BILL BOT STATISTICS**\n\n"
        f"👥 **Total Users:** {user_count}\n"
        f"💰 **Bill Categories:** {len(ALL_BILLS)}\n"
        f"📍 **States Covered:** 50/50 USA\n"
        f"⚡ **Specialized States:** {len(STATE_BILL_SPECIALTIES)}\n\n"
        f"📈 **Growth:** +{min(user_count, 500)} today\n"
        f"⏰ **Status:** ✅ Active 24/7\n"
        f"📞 **Contacts:** @BillSavingsExpert, @BillHelperUSA\n\n"
        f"*50% OFF All Bills USA Bot*"
    )
    
    bot.send_message(ADMIN_ID, stats_message, parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Admin only.")
        return
    
    if len(broadcast_users) == 0:
        bot.reply_to(message, "No users yet.")
        return
    
    msg = bot.send_message(
        ADMIN_ID, 
        f"📤 Send bill discount alert to {len(broadcast_users)} users:\n\n"
        f"Type your 50% OFF bill deal:"
    )
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if hasattr(message, 'is_broadcast_processed') and message.is_broadcast_processed:
        return
    
    message.is_broadcast_processed = True
    broadcast_text = message.text
    users = list(broadcast_users)
    success_count = 0
    
    status_msg = bot.send_message(ADMIN_ID, f"📤 Sending to {len(users)} users...")
    
    for user_id in users:
        try:
            notification = (
                f"🔥 **50% OFF BILL ALERT** 🔥\n\n"
                f"{broadcast_text}\n\n"
                f"📍 All 50 states covered\n"
                f"💰 Guaranteed 50% OFF all bills\n"
                f"📞 Contact @BillSavingsExpert now!\n"
                f"📞 Or @BillHelperUSA for support"
            )
            bot.send_message(user_id, notification)
            success_count += 1
        except Exception:
            pass
    
    bot.edit_message_text(
        f"✅ **Bill Alert Sent!**\n\n"
        f"📊 **Results:**\n"
        f"• ✅ Success: {success_count} users\n"
        f"• 📊 Total: {len(users)} users\n\n"
        f"*50% OFF bill deal delivered!*",
        ADMIN_ID,
        status_msg.message_id
    )

# ===== DEFAULT HANDLER =====
@bot.message_handler(func=lambda message: True)
def all_messages_handler(message):
    user_id = message.from_user.id
    broadcast_users.add(user_id)
    
    if message.text and message.text.lower() in ['hi', 'hello', 'hey', '/start']:
        return
    
    if not message.text.startswith('/'):
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📞 Contact @BillSavingsExpert", url="https://t.me/BillSavingsExpert"),
            types.InlineKeyboardButton("📞 Contact @BillHelperUSA", url="https://t.me/BillHelperUSA")
        )
        markup.add(
            types.InlineKeyboardButton("🚀 Start Bot", callback_data="back_main"),
            types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/flights_bills_b4u")
        )
        
        bot.send_message(
            message.chat.id,
            "🔥 **HALF OFF ALL BILLS USA** 🔥\n\n"
            "🎯 **Get 50% OFF on EVERY bill:**\n"
            "• ⚡ Utilities: Electric, Gas, Water\n"
            "• 📱 Internet, Phone, Cable, Streaming\n"
            "• 🏠 Rent, Mortgage, HOA, Property Tax\n"
            "• 💳 Credit Cards, Loans, Medical Bills\n"
            "• 🛡️ Insurance: Health, Car, Home, Life\n"
            "• 📦 Child Care, Education, Pets, Gym\n\n"
            "📍 **Coverage:** All 50 USA States\n"
            "💰 **Guarantee:** Pay ONLY 50%\n"
            "⏰ **Service:** 24/7 Emergency Help\n\n"
            "📞 **Contact for immediate bill help:**\n"
            "• @BillSavingsExpert (Primary)\n"
            "• @BillHelperUSA (Support)\n"
            "• @flights_bills_b4u (Updates)\n\n"
            "Click buttons below or type /start!",
            reply_markup=markup,
            parse_mode='Markdown'
        )

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- SEO Meta Tags -->
    <title>50% OFF All Bills USA | Pay Half for Every Bill | Bill Discount Service</title>
    <meta name="description" content="Get 50% OFF all your bills: electricity, gas, water, internet, phone, rent, mortgage, credit cards, loans, insurance, medical bills. All 50 states covered. Pay only half!">
    <meta name="keywords" content="half off bills, 50% off utility bills, pay half electricity bill, reduce water bill, cheap internet service, discount cable TV, credit card bill help, student loan assistance, medical bill reduction, rent assistance, mortgage help, insurance discount, all bills 50% off, USA bill help">
    
    <!-- Open Graph -->
    <meta property="og:title" content="50% OFF All Bills USA - Pay Only Half">
    <meta property="og:description" content="Guaranteed 50% discount on electricity, water, gas, internet, phone, rent, credit cards, loans, insurance, medical bills. All 50 states.">
    <meta property="og:type" content="website">
    
    <!-- Schema.org -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Service",
      "name": "50% OFF All Bills USA",
      "description": "50% discount service for all utility bills, communication bills, housing costs, debt payments, insurance premiums, and medical bills across all 50 USA states.",
      "areaServed": {
        "@type": "Country",
        "name": "United States"
      },
      "serviceType": "Bill Payment Assistance"
    }
    </script>
    
    <style>
        body { font-family: 'Arial', sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .header { text-align: center; margin-bottom: 60px; }
        .discount-badge { background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); color: white; padding: 25px 50px; border-radius: 60px; font-size: 42px; font-weight: bold; display: inline-block; margin: 30px 0; box-shadow: 0 15px 35px rgba(255, 65, 108, 0.4); text-transform: uppercase; letter-spacing: 2px; }
        .bill-categories { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 30px; margin: 50px 0; }
        .bill-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); padding: 30px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2); transition: transform 0.3s; }
        .bill-card:hover { transform: translateY(-10px); background: rgba(255, 255, 255, 0.15); }
        .bill-icon { font-size: 50px; margin-bottom: 20px; }
        .states-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 40px 0; }
        .state-card { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.1); }
        .contact-section { background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%); padding: 50px; border-radius: 25px; margin: 60px 0; text-align: center; }
        .contact-button { display: inline-block; background: white; color: #2a5298; padding: 18px 40px; margin: 15px; border-radius: 15px; text-decoration: none; font-weight: bold; font-size: 18px; transition: all 0.3s; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        .contact-button:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.3); background: #f8f9fa; }
        .keyword-list { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; margin: 40px 0; }
        .keyword-tag { background: rgba(255, 255, 255, 0.15); padding: 10px 20px; border-radius: 25px; font-size: 14px; }
        @media (max-width: 768px) {
            .discount-badge { font-size: 32px; padding: 20px 35px; }
            .bill-categories { grid-template-columns: 1fr; }
            .contact-button { display: block; margin: 15px auto; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="font-size: 3em; margin-bottom: 10px;">🔥 50% OFF ALL BILLS USA 🔥</h1>
            <p style="font-size: 1.5em; opacity: 0.9;">Pay Only Half for Every Bill - All 50 States Covered</p>
            <div class="discount-badge">50% OFF ALL BILLS</div>
            <p style="font-size: 1.2em; max-width: 800px; margin: 0 auto 30px; line-height: 1.6;">
                Electricity • Gas • Water • Internet • Phone • Cable • Streaming • Credit Cards • 
                Loans • Insurance • Rent • Mortgage • Medical • Child Care • Education • Pets
            </p>
        </div>
        
        <div class="bill-categories">
            <div class="bill-card">
                <div class="bill-icon">⚡</div>
                <h3>Utility Bills 50% OFF</h3>
                <p>Electricity, Natural Gas, Water & Sewer, Trash Collection, Heating Oil, Propane. All providers covered nationwide.</p>
            </div>
            <div class="bill-card">
                <div class="bill-icon">🌐</div>
                <h3>Internet & Phone 50% OFF</h3>
                <p>Comcast, Verizon, AT&T, Spectrum, T-Mobile, all mobile plans, landlines, business phones, satellite internet.</p>
            </div>
            <div class="bill-card">
                <div class="bill-icon">📺</div>
                <h3>Cable & Streaming 50% OFF</h3>
                <p>DIRECTV, DISH, Xfinity TV, Netflix, Disney+, Hulu, Amazon Prime, HBO Max, all streaming services.</p>
            </div>
            <div class="bill-card">
                <div class="bill-icon">💳</div>
                <h3>Credit Cards 50% OFF</h3>
                <p>Chase, Bank of America, Citi, Capital One, American Express, Discover, all store cards, minimum payment help.</p>
            </div>
            <div class="bill-card">
                <div class="bill-icon">🏦</div>
                <h3>All Loans 50% OFF</h3>
                <p>Student loans, personal loans, auto loans, mortgage payments, payday loans, business loans, SBA loans.</p>
            </div>
            <div class="bill-card">
                <div class="bill-icon">🛡️</div>
                <h3>Insurance 50% OFF</h3>
                <p>Health insurance, car insurance, home insurance, life insurance, business insurance, all premiums reduced.</p>
            </div>
            <div class="bill-card">
                <div class="bill-icon">🏠</div>
                <h3>Rent & Housing 50% OFF</h3>
                <p>Apartment rent, house rent, mortgage payments, HOA fees, property taxes, commercial rent assistance.</p>
            </div>
            <div class="bill-card">
                <div class="bill-icon">🏥</div>
                <h3>Medical Bills 50% OFF</h3>
                <p>Hospital bills, doctor bills, dental bills, prescription drugs, medical equipment, therapy, ambulance.</p>
            </div>
        </div>
        
        <div style="text-align: center; margin: 60px 0;">
            <h2 style="font-size: 2.5em; margin-bottom: 30px;">📍 All 50 USA States Covered</h2>
            <div class="states-grid">
                <div class="state-card">California</div>
                <div class="state-card">Texas</div>
                <div class="state-card">New York</div>
                <div class="state-card">Florida</div>
                <div class="state-card">Illinois</div>
                <div class="state-card">Pennsylvania</div>
                <div class="state-card">Ohio</div>
                <div class="state-card">Georgia</div>
                <div class="state-card">All 50 States →</div>
            </div>
        </div>
        
        <div class="keyword-list">
            <span class="keyword-tag">half off electricity bill</span>
            <span class="keyword-tag">50% off water bill</span>
            <span class="keyword-tag">cheap internet service</span>
            <span class="keyword-tag">discount cable TV</span>
            <span class="keyword-tag">credit card bill help</span>
            <span class="keyword-tag">student loan assistance</span>
            <span class="keyword-tag">medical bill reduction</span>
            <span class="keyword-tag">rent assistance 50% off</span>
            <span class="keyword-tag">mortgage payment help</span>
            <span class="keyword-tag">insurance premium discount</span>
            <span class="keyword-tag">all bills 50% off</span>
            <span class="keyword-tag">USA bill help</span>
        </div>
        
        <div class="contact-section">
            <h2 style="font-size: 2.8em; margin-bottom: 30px;">📞 Get 50% OFF Your Bills Now!</h2>
            <p style="font-size: 1.3em; margin-bottom: 40px; max-width: 800px; margin-left: auto; margin-right: auto;">
                Stop overpaying! We pay 100% of your bills - you pay only 50%.<br>
                All 50 states • 24/7 service • Guaranteed savings
            </p>
            
            <a href="https://t.me/BillSavingsExpert" class="contact-button">
                📞 Contact @BillSavingsExpert
            </a>
            
            <a href="https://t.me/BillHelperUSA" class="contact-button">
                📞 Contact @BillHelperUSA
            </a>
            
            <a href="https://t.me/flights_bills_b4u" class="contact-button">
                📢 Join @flights_bills_b4u
            </a>
            
            <div style="margin-top: 40px; font-size: 1.2em;">
                <p>✅ 50% OFF Guaranteed • 📍 All 50 States</p>
                <p>⏰ 24/7 Emergency Service • 💰 No Hidden Fees</p>
            </div>
        </div>
        
        <footer style="text-align: center; margin-top: 80px; padding-top: 40px; border-top: 1px solid rgba(255, 255, 255, 0.2);">
            <p style="font-size: 1.1em;">© 2024 50% OFF All Bills USA. All rights reserved.</p>
            <p style="opacity: 0.8; margin-top: 10px;">Guaranteed 50% discount on all bills across all 50 United States.</p>
            <p style="margin-top: 20px; font-size: 0.9em; opacity: 0.6;">
                Service available for residential and commercial customers. Terms and conditions apply.
                Not affiliated with any utility or service provider. Independent bill payment assistance service.
            </p>
        </footer>
    </div>
</body>
</html>
    """

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = request.get_data().decode("utf-8")
    update_obj = telebot.types.Update.de_json(update)
    bot.process_new_updates([update_obj])
    return "OK", 200

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Token required")
    
    try:
        bot.remove_webhook()
        render_domain = os.environ.get("RENDER_EXTERNAL_URL")
        
        if render_domain:
            webhook_url = f"{render_domain}/{TOKEN}"
            bot.set_webhook(url=webhook_url)
            print(f"🔥 **50% OFF ALL BILLS BOT DEPLOYED**")
            print(f"💰 Discount: 50% OFF ALL BILLS")
            print(f"📍 Coverage: All 50 USA States")
            print(f"📊 Bill Categories: {len(ALL_BILLS)} comprehensive types")
            print(f"⚡ Specialized States: {len(STATE_BILL_SPECIALTIES)} state-specific programs")
            print(f"📞 Primary Contact: @BillSavingsExpert")
            print(f"📞 Support Contact: @BillHelperUSA")
            print(f"📢 Updates Channel: @flights_bills_b4u")
            print(f"👑 Admin ID: {ADMIN_ID}")
            print(f"🚀 Bot Ready for FAST RANKING!")
        else:
            print("🔧 Running in polling mode (development)")
            
    except Exception as e:
        print(f"⚠️ Webhook setup: {e}")
    
    print("\n" + "="*60)
    print("🔥 **SEO OPTIMIZATION SUMMARY:**")
    print("="*60)
    print("✅ Primary Keywords: half off bills, 50% off utility bills")
    print("✅ Secondary: pay half electricity bill, reduce water bill")
    print("✅ Location-Based: all 50 states coverage highlighted")
    print("✅ Long-Tail: credit card bill help, student loan assistance")
    print("✅ Service-Specific: medical bill reduction, rent assistance")
    print("✅ Commercial: business bills, commercial rent, insurance")
    print("✅ Emergency: 24/7 service, same-day help, emergency bills")
    print("="*60)
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
