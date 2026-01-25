from gpt4all import GPT4All
import re
import json


# ============================================
# BASE DE CONNAISSANCES - AIRLINE LOYALTY PROGRAM
# ============================================

AIRLINE_KNOWLEDGE = {
    
    # ============================================
    # DURÉES DE VOL (en heures:minutes)
    # ============================================
    "flight_durations": {
        # Vols domestiques Canada
        ("toronto", "vancouver"): "4h30",
        ("vancouver", "toronto"): "4h15",
        ("toronto", "montreal"): "1h20",
        ("montreal", "toronto"): "1h15",
        ("toronto", "calgary"): "4h00",
        ("calgary", "toronto"): "3h45",
        ("vancouver", "montreal"): "5h00",
        ("montreal", "vancouver"): "5h15",
        ("toronto", "halifax"): "2h15",
        ("calgary", "vancouver"): "1h20",
        ("winnipeg", "toronto"): "2h30",
        ("ottawa", "vancouver"): "5h00",
        ("quebec city", "toronto"): "1h30",
        ("edmonton", "toronto"): "4h00",
        ("saskatoon", "vancouver"): "2h00",
        
        # Vols internationaux - Europe
        ("toronto", "london"): "7h00",
        ("london", "toronto"): "8h00",
        ("toronto", "paris"): "7h30",
        ("paris", "toronto"): "8h15",
        ("montreal", "paris"): "6h45",
        ("paris", "montreal"): "7h30",
        ("toronto", "frankfurt"): "8h00",
        ("toronto", "rome"): "9h00",
        ("toronto", "amsterdam"): "7h15",
        ("toronto", "madrid"): "8h00",
        ("toronto", "dublin"): "6h30",
        ("vancouver", "london"): "9h30",
        ("montreal", "london"): "6h30",
        ("toronto", "barcelona"): "8h30",
        ("toronto", "zurich"): "8h00",
        ("toronto", "lisbon"): "7h00",
        
        # Vols internationaux - USA
        ("toronto", "new york"): "1h30",
        ("new york", "toronto"): "1h35",
        ("toronto", "los angeles"): "5h00",
        ("los angeles", "toronto"): "4h30",
        ("toronto", "miami"): "3h15",
        ("vancouver", "seattle"): "0h50",
        ("montreal", "boston"): "1h20",
        ("toronto", "chicago"): "1h45",
        ("calgary", "san francisco"): "2h45",
        ("toronto", "atlanta"): "2h30",
        ("toronto", "las vegas"): "4h30",
        ("montreal", "new york"): "1h20",
        ("vancouver", "los angeles"): "2h45",
        ("toronto", "orlando"): "3h00",
        ("toronto", "washington dc"): "1h30",
        ("toronto", "dallas"): "3h30",
        ("toronto", "houston"): "3h45",
        
        # Vols internationaux - Asie
        ("toronto", "tokyo"): "13h00",
        ("vancouver", "tokyo"): "9h30",
        ("toronto", "beijing"): "13h30",
        ("vancouver", "hong kong"): "12h00",
        ("toronto", "delhi"): "14h00",
        ("toronto", "seoul"): "13h30",
        ("vancouver", "shanghai"): "11h00",
        ("toronto", "singapore"): "18h00",
        ("vancouver", "seoul"): "10h00",
        ("toronto", "bangkok"): "17h00",
        
        # Vols internationaux - Amérique Latine
        ("toronto", "mexico city"): "4h30",
        ("toronto", "cancun"): "4h00",
        ("toronto", "sao paulo"): "10h30",
        ("toronto", "buenos aires"): "11h00",
        ("toronto", "lima"): "7h30",
        ("toronto", "bogota"): "5h30",
        ("vancouver", "mexico city"): "5h00",
        
        # Vols internationaux - Moyen-Orient & Afrique
        ("toronto", "dubai"): "12h30",
        ("toronto", "tel aviv"): "11h00",
        ("toronto", "cairo"): "11h30",
        ("toronto", "johannesburg"): "16h00",
        ("toronto", "casablanca"): "7h30",
        
        # Vols internationaux - Océanie
        ("toronto", "sydney"): "20h00",
        ("vancouver", "sydney"): "15h00",
        ("toronto", "auckland"): "18h00",
        ("vancouver", "auckland"): "13h00",
    },
    
    # ============================================
    # INFORMATIONS SUR LES DESTINATIONS
    # ============================================
    "destinations": {
        "toronto": {
            "timezone": "EST (UTC-5)",
            "airport_code": "YYZ",
            "airport_name": "Toronto Pearson International",
            "weather_summer": "25-30°C",
            "weather_winter": "-5 to 0°C",
            "peak_season": "Summer (June-August)",
            "attractions": ["CN Tower", "Royal Ontario Museum", "Distillery District"]
        },
        "paris": {
            "timezone": "CET (UTC+1)",
            "airport_code": "CDG",
            "airport_name": "Charles de Gaulle",
            "weather_summer": "20-25°C",
            "weather_winter": "3-7°C",
            "peak_season": "Spring/Summer (April-September)",
            "attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame"]
        },
        "tokyo": {
            "timezone": "JST (UTC+9)",
            "airport_code": "NRT/HND",
            "airport_name": "Narita/Haneda",
            "weather_summer": "26-32°C",
            "weather_winter": "5-10°C",
            "peak_season": "Spring (Cherry Blossoms - March-April)",
            "attractions": ["Senso-ji Temple", "Shibuya Crossing", "Mount Fuji"]
        },
        # Ajoutez d'autres destinations selon vos besoins
    },
    
    # ============================================
    # CONFIGURATION DES SIÈGES
    # ============================================
    "seat_info": {
        "narrow_body": {  # Boeing 737, A320 (vols domestiques/courts)
            "aircraft_types": ["Boeing 737-800", "Airbus A320"],
            "window_seats": ["A", "F"],
            "aisle_seats": ["C", "D"],
            "middle_seats": ["B", "E"],
            "total_columns": 6,
            "total_rows": 30,
            "rows": {
                "1-5": "First Class",
                "6-10": "Premium Economy",
                "11-30": "Economy"
            },
            "exit_rows": [12, 13, 26],
            "bulkhead_rows": [1, 6, 11],
            "best_seats": ["12A", "12F", "13C", "13D", "1A", "1F"],
            "worst_seats": ["30B", "30E", "15B", "15E", "11B", "11E"],
            "seat_width": {
                "first_class": "21 inches",
                "premium_economy": "18.5 inches",
                "economy": "17.2 inches"
            },
            "recline": {
                "first_class": "6 inches",
                "premium_economy": "5 inches",
                "economy": "3 inches"
            }
        },
        
        "wide_body": {  # Boeing 787, A350 (vols internationaux)
            "aircraft_types": ["Boeing 787-9", "Airbus A350-900"],
            "window_seats": ["A", "K"],
            "aisle_seats": ["C", "D", "G", "H"],
            "middle_seats": ["B", "E", "F", "J"],
            "total_columns": 10,
            "total_rows": 40,
            "layout": "3-4-3",
            "rows": {
                "1-4": "Business Class (lie-flat)",
                "5-10": "Premium Economy",
                "11-40": "Economy"
            },
            "exit_rows": [15, 16, 30],
            "bulkhead_rows": [1, 5, 11],
            "best_seats": ["1A", "1K", "15D", "15G", "5A", "5K"],
            "worst_seats": ["40E", "40F", "25B", "25J", "11E", "11F"],
            "seat_width": {
                "business_class": "22 inches (converts to 78\" bed)",
                "premium_economy": "19 inches",
                "economy": "17.5 inches"
            },
            "recline": {
                "business_class": "180° (lie-flat)",
                "premium_economy": "7 inches",
                "economy": "4 inches"
            }
        },
        
        "seat_pitch": {
            "first_class": "40-42 inches",
            "business_class": "60-78 inches (lie-flat)",
            "premium_economy": "35-38 inches",
            "economy": "31-32 inches",
            "economy_extra_legroom": "34-36 inches"
        },
        
        "seat_features": {
            "first_class": ["Priority boarding", "Dedicated overhead bin", "Power outlet", "Premium amenity kit"],
            "business_class": ["Lie-flat bed", "Direct aisle access", "Power + USB", "Noise-cancelling headphones", "Premium bedding"],
            "premium_economy": ["Extra legroom", "Wider seat", "Power outlet", "Enhanced meal service"],
            "economy": ["Standard comfort", "USB port", "Personal entertainment screen"],
        }
    },
    
    # ============================================
    # TARIFS ET UPGRADES
    # ============================================
    "pricing": {
        "upgrades": {
            "premium_economy": {
                "price": 7500,
                "benefits": [
                    "Extra 4-6 inches legroom (35-38\" pitch)",
                    "Priority boarding (Group 2)",
                    "Enhanced meal service with choice",
                    "Larger personal screen (12 inches)",
                    "Dedicated overhead bin space",
                    "Power outlet at every seat"
                ]
            },
            "business_class": {
                "price": 20000,
                "benefits": [
                    "Lie-flat seat (converts to 78\" bed)",
                    "Priority check-in and boarding",
                    "Complimentary lounge access",
                    "Gourmet multi-course meals",
                    "Premium beverages (champagne, wine)",
                    "18-inch 4K entertainment screen",
                    "Noise-cancelling Bose headphones",
                    "Extra baggage allowance (3 bags)",
                    "Amenity kit with skincare products"
                ]
            },
            "first_class": {
                "price": 35000,
                "benefits": [
                    "Private suite with door",
                    "Fully lie-flat bed (80 inches)",
                    "Dedicated flight attendant",
                    "Premium lounge access + spa",
                    "À la carte dining (order anytime)",
                    "Premium champagne and caviar",
                    "Luxury amenity kit",
                    "Chauffeur service (select airports)"
                ]
            },
            "extra_legroom": {
                "price": 2500,
                "benefits": [
                    "3-5 extra inches of legroom",
                    "Early boarding (Group 3)",
                    "Same seat, more space"
                ]
            },
        },

        "seat_selection": {
            "standard": 0,
            "preferred": 1500,  # Front of cabin
            "exit_row": 3000,   # Extra legroom
            "window_bulkhead": 2000,  # Extra space, no under-seat storage
            "aisle_bulkhead": 2000,
        },

        "baggage": {
            "economy": {
                "carry_on": "1 bag (23kg) + 1 personal item included",
                "checked": "1 bag (23kg) included, 2nd bag 4,000 points, 3rd bag 6,000 points",
                "overweight": "Extra 2,000 points per 5kg over limit",
                "oversized": "Extra 3,000 points for sports equipment"
            },
            "premium_economy": {
                "carry_on": "2 bags (23kg each) + 1 personal item",
                "checked": "2 bags (23kg each) included, 3rd bag 4,000 points",
                "priority": "Priority baggage handling"
            },
            "business": {
                "carry_on": "2 bags (32kg each) + 1 personal item",
                "checked": "3 bags (32kg each) included",
                "priority": "First-off carousel",
                "extras": "Golf clubs, skis, bikes included"
            }
        },
        
        "special_items": {
            "musical_instruments": 5000,  # Cello, guitar, etc.
            "sports_equipment": 3000,     # Skis, golf clubs, surfboards
            "bicycle": 4000,
            "pet_carrier": 9500,          # In-cabin
            "extra_seat": 15000,          # For comfort or large item
        }
    },

    # ============================================
    # SERVICES À BORD
    # ============================================
    "services": {
        "wifi": {
            "available": True,
            "pricing": {
                "messaging": 500,      # WhatsApp, iMessage only
                "browsing": 1000,      # Full internet access
                "streaming": 1500,     # HD video streaming
                "full_flight": 2500,   # Unlimited for entire journey
            },
            "free_for": ["Business Class", "First Class", "Star", "Nova", "Aurora"],  # ← Changé ici
            "speed": "Up to 15 Mbps on select aircraft",
            "coverage": "Available on 95% of flights"
        },
        
        "meals": {
            "short_haul": {  # < 2h
                "economy": "Snacks (pretzels, cookies) + complimentary beverages (soft drinks, coffee, tea)",
                "premium": "Light meal box (sandwich or wrap) + snacks + beverages",
                "business": "Fresh meal platter + premium beverages + dessert"
            },
            "medium_haul": {  # 2-6h
                "economy": "Hot meal (chicken or pasta) + bread + dessert + beverages",
                "premium": "Choice of 2 entrées + appetizer + dessert + wine/beer included",
                "business": "3-course meal (appetizer, main, dessert) + premium wine selection"
            },
            "long_haul": {  # > 6h
                "economy": "2 hot meals + mid-flight snack + ice cream + beverages throughout",
                "premium": "2 full meals with choice + snack service + premium drinks + dessert cart",
                "business": "Dine on demand (order anytime) + snack bar + premium champagne + chef-inspired cuisine"
            },
            "special_meals": [
                "Vegetarian (VGML)",
                "Vegan (VGSN)",
                "Gluten-free (GFML)",
                "Kosher (KSML)",
                "Halal (MOML)",
                "Diabetic (DBML)",
                "Child meal (CHML)",
                "Low sodium (LSML)"
            ],
            "request_deadline": "48 hours before departure"
        },
        
        "entertainment": {
            "economy": {
                "screen": "10.6-inch personal touchscreen",
                "content": "200+ movies, 150+ TV shows, 100+ music albums, games",
                "audio": "Standard headphones provided",
                "connectivity": "Bluetooth pairing available on new aircraft"
            },
            "premium": {
                "screen": "12-inch HD touchscreen with enhanced resolution",
                "content": "Premium content library + latest releases",
                "audio": "Noise-cancelling headphones included",
                "extras": "USB charging port + power outlet"
            },
            "business": {
                "screen": "18-inch 4K touchscreen with privacy divider",
                "content": "Exclusive business class content + live TV",
                "audio": "Bose QuietComfort noise-cancelling headphones",
                "extras": "Wireless charging pad + multiple USB ports",
                "control": "Tablet-style remote control"
            }
        },
        
        "power": {
            "economy": "USB-A port at every seat",
            "premium": "USB-A + USB-C + AC power outlet (110V)",
            "business": "USB-A + USB-C + AC outlet + wireless charging pad",
            "note": "Available on 90% of fleet (older aircraft may vary)"
        },
        
        "comfort_items": {
            "economy": ["Pillow", "Blanket (on request)", "Headphones"],
            "premium": ["Premium pillow", "Blanket", "Noise-cancelling headphones", "Amenity kit"],
            "business": ["Memory foam pillow", "Duvet", "Bose headphones", "Luxury amenity kit", "Sleeper suit", "Slippers"]
        }
    },
    
    # ============================================
    # PROGRAMME DE FIDÉLITÉ
    # ============================================
    # Dans AIRLINE_KNOWLEDGE, section "loyalty_program"

    "loyalty_program": {
        "name": "Loyalty Rewards",
        
        "tiers": {
            "2018_promotion": {
                "miles_required": 0,
                "annual_spend": 0,
                "benefits": [
                    "Earn 1x points on flights",
                    "Priority boarding (Group 3)",
                    "Free seat selection 24h before departure",
                    "5% discount on in-flight purchases",
                    "Birthday bonus: 500 points",
                    "Special 2018 promotional member"
                ],
            },
            "star": {
                "miles_required": 25000,
                "annual_spend": 5000,
                "benefits": [
                    "Earn 1.5x points on all purchases",
                    "Priority boarding (Group 2)",
                    "1 free checked bag",
                    "Complimentary WiFi on all flights",
                    "Domestic lounge access",
                    "Free seat selection anytime",
                    "Priority check-in counter",
                    "24/7 dedicated support line",
                    "10% bonus on points redemption"
                ],
            },
            "nova": {
                "miles_required": 50000,
                "annual_spend": 10000,
                "benefits": [
                    "Earn 2x points on everything",
                    "Priority boarding (Group 1)",
                    "2 free checked bags (up to 32kg each)",
                    "Complimentary WiFi + streaming",
                    "International lounge access worldwide",
                    "Free same-day standby",
                    "Complimentary upgrades (space available)",
                    "Dedicated Nova check-in",
                    "Companion upgrade voucher (2 per year)",
                    "15% bonus on redemptions"
                ],
            },
            "aurora": {
                "miles_required": 100000,
                "annual_spend": 25000,
                "benefits": [
                    "Earn 3x points + 50% bonus on international",
                    "First to board (anytime)",
                    "3 free checked bags (up to 32kg each)",
                    "Unlimited complimentary WiFi + guests",
                    "Premium lounge access + 2 guests",
                    "Guaranteed confirmed upgrades (72h advance)",
                    "Complimentary business class on routes over 6h",
                    "Personal travel concierge (24/7)",
                    "VIP meet & greet at major airports",
                    "20% bonus on all redemptions",
                    "Lifetime status qualification credit"
                ],
            }
        },
        
        "status_benefits_comparison": {
            "checked_bags": {"2018_promotion": 0, "star": 1, "nova": 2, "aurora": 3},
            "priority_boarding": {"2018_promotion": "Group 3", "star": "Group 2", "nova": "Group 1", "aurora": "Anytime"},
            "lounge_access": {"2018_promotion": False, "star": "Domestic", "nova": "Worldwide", "aurora": "Premium + guests"},
            "wifi": {"2018_promotion": False, "star": True, "nova": True, "aurora": "Unlimited + guests"},
            "points_earning": {"2018_promotion": "1x", "star": "1.5x", "nova": "2x", "aurora": "3x"},
            "redemption_discount": {"2018_promotion": "0%", "star": "10%", "nova": "15%", "aurora": "20%"}
        }
    },
    
    # ============================================
    # POLITIQUES
    # ============================================
    "policies": {
        "check_in": {
            "online": "24 hours before departure",
            "mobile": "Available via app 24h before",
            "kiosk": "Available at airport 4h before (domestic) / 6h before (international)",
            "counter": "Opens 3 hours before international, 2 hours before domestic",
            "gate_closes": "15 minutes before departure (strictly enforced)",
            "boarding_time": "Boarding begins 45 min before departure",
            "recommended_arrival": {
                "domestic": "90 minutes before departure",
                "international": "3 hours before departure",
                "peak_times": "Add 30-60 minutes during holidays"
            }
        },
        
        "cancellation": {
            "24h_rule": "Free cancellation within 24h of booking (if booked 7+ days before departure)",
            "basic_economy": {
                "refund": "Non-refundable",
                "change_fee": 7500,
                "rebooking": "Same fare class only, pay difference"
            },
            "economy": {
                "refund": "Refundable within 24h of booking",
                "change_fee": 15000,
                "rebooking": "Any fare class, pay difference"
            },
            "premium_economy": {
                "refund": "Partial refund (50% of points)",
                "change_fee": 7500,
                "rebooking": "Flexible, pay difference only"
            },
            "business": {
                "refund": "Fully refundable",
                "change_fee": 0,
                "rebooking": "Unlimited changes, free of charge"
            }
        },
        
        "name_changes": {
            "allowed": "Only for spelling corrections (3 letters max)",
            "fee": 5000,
            "deadline": "24 hours before departure",
            "transfer": "Tickets are non-transferable"
        },

        "minors": {
            "unaccompanied_minor": {
                "age_range": "5-11 years",
                "service_fee": 5000,  # In points
                "service": "Gate-to-gate escort, in-flight supervision",
                "restrictions": "Direct flights only, no connections"
            },
            "young_traveler": {
                "age_range": "12-17 years",
                "service_fee": 2500,  # Optional service
                "service": "Priority boarding and assistance if requested"
            },
            "infant": {
                "age_range": "Under 2 years",
                "lap_infant": "10% of adult fare",
                "infant_seat": "Full child fare for separate seat"
            }
        },
        
        "pets": {
            "in_cabin": {
                "allowed": True,
                "size": "Carrier must fit under seat (45cm x 35cm x 20cm)",
                "max_weight": "10 kg (pet + carrier combined)",
                "fee": 9500,
                "restrictions": "1 pet per passenger, must remain in carrier",
                "advance_booking": "Required 48h minimum",
                "health_certificate": "Required for international flights"
            },
            "cargo": {
                "allowed": True,
                "max_weight": "45 kg (pet + carrier)",
                "fee": 20000,
                "temperature_restrictions": "Not available when temperatures exceed 30°C or below -10°C",
                "crate_requirements": "IATA-compliant hard-sided crate",
                "advance_booking": "72h required"
            },
            "service_animals": {
                "fee": 0,
                "documentation": "Certification required 48h in advance",
                "allowed": "Trained service dogs only",
                "restrictions": "Must remain at handler's feet or on lap"
            },
            "emotional_support": {
                "note": "No longer accepted (policy change 2024)"
            }
        },

        "medical_assistance": {
            "wheelchair": {
                "fee": 0,
                "request": "48 hours advance notice preferred",
                "types": ["Manual wheelchair", "Electric wheelchair", "Aisle chair (onboard)"],
                "battery": "Lithium batteries must meet regulations"
            },
            "oxygen": {
                "allowed": "Personal oxygen concentrators (POC) only",
                "fee": 0,
                "advance": "72h notice + medical certificate required",
                "restrictions": "FAA-approved devices only"
            },
            "medication": {
                "carry_on": "Unlimited, must be declared",
                "storage": "Refrigerated medication can be stored by crew",
                "documentation": "Prescription or doctor's letter recommended"
            },
            "special_seating": {
                "extra_space": "Available for medical needs (no charge with documentation)",
                "bulkhead": "Priority for passengers with limited mobility"
            }
        },
        
        "special_assistance": {
            "wheelchair": "Free service, request 48h in advance",
            "medical_equipment": "Free carry-on allowance (CPAP, oxygen, etc.)",
            "service_animals": "Free of charge, documentation required 48h advance",
            "dietary_requirements": "Request 48h in advance (25+ options available)",
            "language_assistance": "Available in 12 languages",
            "deaf_blind": "Dedicated assistance team available"
        },
        
        "travel_documents": {
            "passport": {
                "validity": "Must be valid 6 months beyond return date (most countries)",
                "blank_pages": "Minimum 2 blank pages required"
            },
            "visa": "Check requirements for destination country",
            "proof_onward": "May be required for entry to certain countries",
            "minors_travel": "Letter of consent required if traveling without both parents"
        }
    },
    
    # ============================================
    # FAQ COURANTES
    # ============================================
    "faq": {
        "can_i_change_my_seat": "Yes! You can change your seat anytime up to check-in via our app or website. Some seats may incur additional points.",
        "whats_included_in_economy": "Economy includes: 1 carry-on bag, 1 checked bag, complimentary meals on flights 2h+, personal entertainment screen, USB charging.",
        "how_do_i_earn_points": "Earn points on flights (1x base rate), plus bonus points with higher membership tiers. Also earn with partner hotels, car rentals, and dining.",
        "can_i_transfer_points": "Yes, to family members (5,000 points minimum, 1,000 point fee per transfer)",
        "do_points_expire": "Points expire after 18 months of account inactivity. Any earning or redemption resets the clock.",
        "whats_the_best_seat": "Exit row seats (12/13 on narrow-body, 15/16 on wide-body) offer extra legroom for 3,000 points.",
        "can_i_bring_food": "Yes, you can bring your own food through security (liquids must be <100ml). Hot meals provided on flights 2h+.",
        "how_early_should_i_arrive": "Domestic: 90 min. International: 3 hours. Add time during peak travel periods.",
        "can_i_get_a_refund": "Depends on fare type. Business class is fully refundable. Economy has varying policies. See cancellation policy.",
        "is_wifi_free": "Free for star, nova, and aurora members. Others: 1,000 points for browsing or 2,500 for full flight.",
    },
    
    # ============================================
    # SEASONAL & PROMOTIONAL
    # ============================================
    "promotions": {
        "current_offers": {
            "double_points": "Earn 2x points on all international flights (Jan-Mar 2026)",
            "companion_bonus": "Book 2+ tickets, get 5,000 bonus points",
            "status_match": "Switch from competitor? We'll match your status + 10,000 points"
        },
        "seasonal_routes": {
            "summer": ["Toronto-Nice", "Vancouver-Reykjavik", "Montreal-Athens"],
            "winter": ["Toronto-Whistler", "Calgary-Aspen", "Montreal-Mont-Tremblant"]
        }
    },
    
    # ============================================
    # AIRPORT INFORMATION
    # ============================================
    "airports": {
        "toronto_yyz": {
            "name": "Toronto Pearson International",
            "terminals": ["Terminal 1", "Terminal 3"],
            "our_terminal": "Terminal 1",
            "lounges": {
                "domestic": "Maple Lounge (Gates B20-B30) - 6am-10pm",
                "international": "Premium Lounge (Gates E70-E80) - 5am-11pm",
                "amenities": ["Buffet", "Shower", "Business center", "Bar"]
            },
            "parking": {
                "terminal": "4,000 points/day",
                "value": "2,500 points/day",
                "economy": "1,500 points/day"
            },
            "transit_time": "Minimum 60 min for international connections",
            "transportation": {
                "UP_Express": "25 min to downtown (150 points)",
                "Taxi": "~5,000 points to downtown",
                "Shuttle": "Partner hotels included"
            }
        },
        "montreal_yul": {
            "name": "Montréal-Trudeau International",
            "terminals": ["Domestic", "International"],
            "our_terminal": "International",
            "lounges": {
                "international": "Transat Lounge (Gates 50-60)"
            }
        },
        "vancouver_yvr": {
            "name": "Vancouver International",
            "terminals": ["Domestic", "International", "South Terminal"],
            "our_terminal": "International",
            "lounges": {
                "domestic": "Pacific Lounge (Gates C)",
                "international": "Zen Lounge (Gates D)"
            }
        }
    },
    
    # ============================================
    # TIPS & RECOMMENDATIONS
    # ============================================
    "travel_tips": {
        "packing": [
            "Pack valuables in carry-on (medication, electronics, jewelry)",
            "Wear heaviest shoes/jacket to save bag weight",
            "Roll clothes to maximize space",
            "Use packing cubes for organization"
        ],
        "comfort": [
            "Stay hydrated (drink 8oz water per flight hour)",
            "Move around every 2 hours on long flights",
            "Compression socks for flights 6h+",
            "Bring eye mask and noise-cancelling headphones"
        ],
        "security": [
            "Have liquids in clear bag (100ml max each)",
            "Wear slip-on shoes for faster screening",
            "Have boarding pass and ID ready",
            "Put electronics in separate bin"
        ],
        "jet_lag": [
            "Adjust sleep schedule 2-3 days before departure",
            "Stay hydrated, avoid alcohol",
            "Get sunlight upon arrival",
            "Take short naps only (20-30 min max)"
        ]
    },
    
    "currency": "points"
}


# ============================================
# FONCTIONS UTILITAIRES AMÉLIORÉES
# ============================================

def get_flight_duration(origin: str, destination: str) -> str:
    """Retourne la durée du vol entre deux villes"""
    origin = origin.lower().strip()
    destination = destination.lower().strip()
    
    for (o, d), duration in AIRLINE_KNOWLEDGE["flight_durations"].items():
        if (origin in o and destination in d) or (destination in o and origin in d):
            return duration
    
    return "unknown"


def get_destination_info(city: str) -> dict:
    """Retourne les informations sur une destination"""
    city = city.lower().strip()
    return AIRLINE_KNOWLEDGE["destinations"].get(city, {})


def check_window_seat(seat: str, aircraft_type: str = "narrow_body") -> bool:
    """Vérifie si c'est un siège fenêtre"""
    if not seat or len(seat) < 2:
        return False
    seat_letter = seat[-1].upper()
    window_seats = AIRLINE_KNOWLEDGE["seat_info"][aircraft_type]["window_seats"]
    return seat_letter in window_seats


def get_seat_type(seat: str, aircraft_type: str = "narrow_body") -> str:
    """Retourne le type de siège (window/aisle/middle)"""
    if not seat or len(seat) < 2:
        return "unknown"
    
    seat_letter = seat[-1].upper()
    seat_config = AIRLINE_KNOWLEDGE["seat_info"][aircraft_type]
    
    if seat_letter in seat_config["window_seats"]:
        return "window"
    elif seat_letter in seat_config["aisle_seats"]:
        return "aisle"
    elif seat_letter in seat_config["middle_seats"]:
        return "middle"
    return "unknown"


def get_seat_recommendations(preferences: list = None, aircraft_type: str = "narrow_body") -> list:
    """Recommande les meilleurs sièges selon les préférences"""
    seat_config = AIRLINE_KNOWLEDGE["seat_info"][aircraft_type]
    
    if not preferences:
        return seat_config["best_seats"]
    
    recommendations = []
    
    if "window" in preferences:
        recommendations.extend([s for s in seat_config["best_seats"] if s[-1] in seat_config["window_seats"]])
    if "aisle" in preferences:
        recommendations.extend([s for s in seat_config["best_seats"] if s[-1] in seat_config["aisle_seats"]])
    if "extra legroom" in preferences or "legroom" in preferences:
        recommendations.extend([f"{row}A" for row in seat_config["exit_rows"]])
    
    return recommendations if recommendations else seat_config["best_seats"]


def is_exit_row(seat: str, aircraft_type: str = "narrow_body") -> bool:
    """Vérifie si c'est un siège rangée de sortie"""
    if not seat or len(seat) < 2:
        return False
    
    try:
        row_number = int(re.match(r"(\d+)", seat).group(1))
        exit_rows = AIRLINE_KNOWLEDGE["seat_info"][aircraft_type]["exit_rows"]
        return row_number in exit_rows
    except:
        return False


def get_loyalty_tier_info(tier: str) -> dict:
    """Retourne les infos d'un niveau de fidélité"""
    return AIRLINE_KNOWLEDGE["loyalty_program"]["tiers"].get(tier.lower(), {})


def get_next_tier_requirements(current_tier: str = "2018_promotion") -> dict:
    """Calcule combien de points manquent pour le prochain niveau"""
    # Nouvel ordre des tiers
    tiers_order = ["2018_promotion", "star", "nova", "aurora"]
    current_tier = current_tier.lower()
    
    if current_tier not in tiers_order:
        return {}
    
    current_index = tiers_order.index(current_tier)
    
    if current_index >= len(tiers_order) - 1:
        return {"message": "You're already at the highest tier (Aurora)!"}
    
    next_tier = tiers_order[current_index + 1]
    next_tier_info = AIRLINE_KNOWLEDGE["loyalty_program"]["tiers"][next_tier]
    current_tier_info = AIRLINE_KNOWLEDGE["loyalty_program"]["tiers"][current_tier]
    
    points_needed = next_tier_info["miles_required"] - current_tier_info["miles_required"]
    
    return {
        "next_tier": next_tier,
        "points_needed": points_needed,
        "annual_spend_needed": next_tier_info["annual_spend"],
        "new_benefits": next_tier_info["benefits"]
    }


def get_baggage_allowance(cabin_class: str) -> dict:
    """Retourne les franchises bagages"""
    return AIRLINE_KNOWLEDGE["pricing"]["baggage"].get(cabin_class.lower(), {})


def get_upgrade_price(upgrade_type: str) -> dict:
    """Retourne le prix d'un upgrade"""
    return AIRLINE_KNOWLEDGE["pricing"]["upgrades"].get(upgrade_type, {})


def calculate_points_for_flight(origin: str, destination: str, cabin_class: str = "economy") -> int:
    """Estime les points nécessaires pour un vol"""
    duration = get_flight_duration(origin, destination)
    
    if duration == "unknown":
        return 0
    
    # Convertir durée en minutes
    hours = int(duration.split("h")[0])
    
    # Classification par distance
    if hours < 2:
        category = "domestic_short"
    elif hours < 6:
        category = "domestic_medium"
    elif hours < 10:
        category = "europe"
    else:
        category = "asia"
    
    redemption = AIRLINE_KNOWLEDGE["loyalty_program"]["redemption"]["flights"]
    
    if category in redemption:
        return redemption[category].get(cabin_class, 0)
    
    return 0


def get_meal_service(flight_duration_hours: float, cabin_class: str = "economy") -> str:
    """Retourne le service de repas selon la durée et la classe"""
    meals = AIRLINE_KNOWLEDGE["services"]["meals"]
    
    if flight_duration_hours < 2:
        return meals["short_haul"].get(cabin_class, meals["short_haul"]["economy"])
    elif flight_duration_hours < 6:
        return meals["medium_haul"].get(cabin_class, meals["medium_haul"]["economy"])
    else:
        return meals["long_haul"].get(cabin_class, meals["long_haul"]["economy"])


def search_faq(query: str) -> list:
    """Recherche dans les FAQ"""
    query = query.lower()
    faq = AIRLINE_KNOWLEDGE["faq"]
    
    results = []
    for question, answer in faq.items():
        if any(word in question.lower() or word in answer.lower() for word in query.split()):
            results.append({"question": question.replace("_", " ").title(), "answer": answer})
    
    return results


def format_points(points: int) -> str:
    """Formate les points avec séparateur de milliers"""
    return f"{points:,} points"


def get_travel_tip(category: str = None) -> list:
    """Retourne des conseils de voyage"""
    tips = AIRLINE_KNOWLEDGE["travel_tips"]
    
    if category and category in tips:
        return tips[category]
    
    # Retourne tous les conseils
    all_tips = []
    for cat, tip_list in tips.items():
        all_tips.extend(tip_list)
    return all_tips


from pathlib import Path
import os

MODEL_PATH = Path(__file__).parent / "mistral-7b-openorca.gguf2.Q4_0.gguf"

try:
    mini_model = GPT4All(str(MODEL_PATH), allow_download=False)
    print(f"✅ GPT4All chargé : {os.path.basename(MODEL_PATH)}")
except Exception as e:
    print(f"❌ Erreur chargement GPT4All : {e}")
    mini_model = None




def extract_entities(user_text: str) -> dict:
    """Extrait les entités du message utilisateur"""
    entities = {
        "seat": None,
        "intent": None,
        "keywords": [],
        "cities": [],
        "is_airline_related": False
    }
    
    # Détecter siège
    seat_patterns = [
        r"\b(\d{1,2}[A-K])\b",
        r"seat\s+(\d{1,2}[A-K])",
        r"i\s+have\s+(?:seat\s+)?(\d{1,2}[A-K])",
    ]
    
    for pattern in seat_patterns:
        match = re.search(pattern, user_text, re.IGNORECASE)
        if match:
            entities["seat"] = match.group(1).upper()
            entities["is_airline_related"] = True
            break
    
    # Détecter villes
    all_cities = set()
    for (city1, city2) in AIRLINE_KNOWLEDGE["flight_durations"].keys():
        all_cities.add(city1)
        all_cities.add(city2)
    
    for city in all_cities:
        if city in user_text.lower():
            entities["cities"].append(city)
            entities["is_airline_related"] = True
    
    # Mots-clés liés à l'aviation
    airline_keywords = [
        "flight", "seat", "upgrade", "baggage", "luggage", "boarding", 
        "check-in", "gate", "terminal", "airport", "lounge", "wifi",
        "meal", "loyalty", "points", "miles", "rewards", "business class",
        "premium", "economy", "first class", "aisle", "window", "pet",
        "cancel", "refund", "booking", "reservation", "plane", "aircraft"
    ]
    
    user_lower = user_text.lower()
    if any(kw in user_lower for kw in airline_keywords):
        entities["is_airline_related"] = True
    
    # Détecter intentions (seulement si lié à l'aviation)
    if entities["is_airline_related"]:
        intent_keywords = {
            "flight_duration": ["duration", "how long", "flight time", "take to fly"],
            "window_seat": ["window", "view", "next to window", "window seat"],
            "seat_type": ["what kind", "type of seat", "aisle", "middle"],
            "upgrade": ["upgrade", "better seat", "premium", "business", "first class"],
            "baggage": ["baggage", "luggage", "bag", "checked bag", "carry-on"],
            "wifi": ["wifi", "internet", "online", "connectivity"],
            "meals": ["meal", "food", "drink", "beverage", "dining"],
            "loyalty": ["points", "miles", "rewards", "status", "tier", "star", "nova"],
            "lounge": ["lounge", "lounge access", "priority pass"],
            "check_in": ["check in", "check-in", "boarding", "gate"],
            "cancellation": ["cancel", "refund", "change flight", "reschedule"],
            "pet": ["pet", "dog", "cat", "animal"],
            "yes": ["yes", "yeah", "sure", "ok", "okay", "please"],
            "no": ["no", "nope", "not now", "maybe later"],
        }
        
        for intent, keywords in intent_keywords.items():
            if any(kw in user_lower for kw in keywords):
                entities["intent"] = intent
                entities["keywords"].extend([kw for kw in keywords if kw in user_lower])
                break
    
    return entities


def build_airline_response(entities: dict, state: dict) -> str:
    """Réponses précises basées sur la base de connaissances airline"""
    intent = entities.get("intent")
    response = None
    
    # 1️⃣ DURÉE DE VOL
    if intent == "flight_duration" and len(entities["cities"]) >= 2:
        origin, destination = entities["cities"][:2]
        duration = get_flight_duration(origin, destination)
        
        if duration != "unknown":
            response = f"The flight from {origin.title()} to {destination.title()} takes approximately {duration}."
        else:
            response = f"I don't have the exact duration for {origin.title()} to {destination.title()} in my database. This route may not be available or requires a connection."
    
    # 2️⃣ TYPE DE SIÈGE
    elif (intent in ["window_seat", "seat_type"]) and entities["seat"]:
        seat = entities["seat"]
        seat_type = get_seat_type(seat, "narrow_body")
        
        if seat_type == "window":
            response = f"Yes! Seat {seat} is a window seat. You'll have a great view during your flight."
        elif seat_type == "aisle":
            response = f"Seat {seat} is an aisle seat, offering easy access and extra space to stretch."
        elif seat_type == "middle":
            window_seats = ', '.join(AIRLINE_KNOWLEDGE['seat_info']['narrow_body']['window_seats'])
            aisle_seats = ', '.join(AIRLINE_KNOWLEDGE['seat_info']['narrow_body']['aisle_seats'])
            response = f"Seat {seat} is a middle seat. Would you like to change to a window seat ({window_seats}) or aisle seat ({aisle_seats})?"
    
    # 3️⃣ BAGAGES
    elif intent == "baggage":
        cabin_class = state.get("cabin_class", "economy")
        baggage_info = get_baggage_allowance(cabin_class)
        
        if baggage_info:
            response = f"For {cabin_class.title()} class:\n"
            response += f"• Carry-on: {baggage_info['carry_on']}\n"
            response += f"• Checked bags: {baggage_info['checked']}"
    
    # 4️⃣ WIFI
    elif intent == "wifi":
        member_tier = state.get("loyalty_tier", "silver")
        
        if member_tier in ["star", "nova", "aurora"]:
            response = f"As a {member_tier.title()} member, you get complimentary WiFi on all flights!"
        else:
            response = "WiFi is available starting at 500 points for messaging, or 1000 points for full browsing."
    
    # 5️⃣ REPAS
    elif intent == "meals":
        response = "Complimentary meals are served on flights over 2 hours. Premium and Business class receive enhanced dining. Special dietary requests can be made 48 hours in advance."
    
    # 6️⃣ PROGRAMME FIDÉLITÉ
    elif intent == "loyalty":
        member_tier = state.get("loyalty_tier", "star")
        tier_info = get_loyalty_tier_info(member_tier)
        
        if tier_info:
            benefits = tier_info["benefits"][:3]
            response = f"As a {member_tier.title()} member, you enjoy:\n• " + "\n• ".join(benefits)
    
    # 7️⃣ UPGRADE
    elif intent == "upgrade":
        seat = state.get("seat", "unknown")
        premium_info = get_upgrade_price("premium_economy")
        business_info = get_upgrade_price("business_class")
        
        response = "I can offer you these upgrade options"
        if seat != "unknown":
            response += f" for seat {seat}"
        response += ":\n\n"
        response += f"1. Premium Economy - {premium_info['price']:,} points\n"
        response += f"   • {premium_info['benefits'][0]}\n"
        response += f"   • {premium_info['benefits'][1]}\n\n"
        response += f"2. Business Class - {business_info['price']:,} points\n"
        response += f"   • {business_info['benefits'][0]}\n"
        response += f"   • {business_info['benefits'][1]}\n\n"
        response += "Which would you prefer?"
    
    # 8️⃣ LOUNGE
    elif intent == "lounge":
        member_tier = state.get("loyalty_tier", "star")
        if member_tier in ["star", "nova", "aurora"]:
            response = f"As a {member_tier.title()} member, you have complimentary lounge access. Show your boarding pass and membership card at the entrance."
        else:
            response = "Lounge access is available for star members and above, or with a day pass for 5,000 points."
    
    # 9️⃣ CHECK-IN
    elif intent == "check_in":
        response = "Online check-in opens 24 hours before departure. For international flights, please arrive 3 hours early. For domestic flights, 2 hours is recommended. Gates close 15 minutes before departure."
    
    # 🔟 ANIMAUX
    elif intent == "pet":
        pet_info = AIRLINE_KNOWLEDGE["policies"]["pets"]["in_cabin"]
        response = f"Small pets (under {pet_info['max_weight']}) can travel in cabin for {pet_info['fee']:,} points. The carrier must fit under the seat. Larger pets travel in cargo for {AIRLINE_KNOWLEDGE['policies']['pets']['cargo']['fee']:,} points."
    
    # 1️⃣1️⃣ ANNULATION
    elif intent == "cancellation":
        response = "Cancellation policies vary by fare type:\n"
        response += "• Basic Economy: Non-refundable, 7,500 points change fee\n"
        response += "• Economy: 15,000 points change fee, refundable within 24h\n"
        response += "• Premium Economy: 7,500 points change fee, partial refund\n"
        response += "• Business: Fully flexible, no fees"
    
    return response


def call_llm(user_text: str, state: dict) -> dict:
    """
    LLM intelligent qui peut parler de TOUT
    """
    print(f"\n🤖 User input: '{user_text}'")
    print(f"📊 Current state: {state}")
    
    # 1️⃣ Extraire entités
    entities = extract_entities(user_text)
    print(f"🔍 Entities: {entities}")
    print(f"✈️ Airline-related: {entities['is_airline_related']}")
    
    # 2️⃣ Mettre à jour l'état
    if entities["seat"]:
        state["seat"] = entities["seat"]
    
    response_text = None
    
    # ============================================
    # CAS 1 : Question liée à l'aviation
    # ============================================
    if entities["is_airline_related"]:
        # Essayer réponse directe de la base de connaissances
        response_text = build_airline_response(entities, state)
        
        # Si pas de réponse directe, utiliser le LLM avec contexte aviation
        if not response_text and mini_model:
            try:
                prompt = f"""You are  a professional airline virtual assistant.

CONTEXT:
- Customer's seat: {state.get('seat', 'unknown')}
- Loyalty tier: {state.get('loyalty_tier', 'star')}
- All prices are in loyalty points (not dollars)

CUSTOMER MESSAGE:
"{user_text}"

RULES:
1. Answer aviation questions with your general knowledge
2. Express ALL costs in "points" (e.g., "7,500 points", never "$75")
3. Be helpful and professional
4. Keep responses brief (2-3 sentences)
5. If you don't know, be honest and suggest general aviation advice

YOUR RESPONSE:"""
                
                response_text = mini_model.generate(
                    prompt,
                    max_tokens=150,
                    temp=0.6,
                    top_k=30,
                    top_p=0.9
                ).strip()
                
                # Nettoyer
                response_text = clean_response(response_text)
                
                print(f"✅ LLM (aviation): {response_text}")
                
            except Exception as e:
                print(f"❌ LLM error: {e}")
                response_text = "I can help with flight information, seats, upgrades, baggage, and loyalty rewards. What would you like to know?"
    
    # ============================================
    # CAS 2 : Question générale (hors aviation)
    # ============================================
    else:
        if mini_model:
            try:
                prompt = f"""
You are a professional airline virtual assistant.

You are ONLY allowed to discuss the following topics:

- Flights
- Seats
- Upgrades
- Loyalty points
- WiFi
- Baggage
- Pets
- Lounge access
- Reservations and booking related to flights
- General travel with this airline

You MAY ALSO respond to:
- Greetings (hello, hi, bonjour)
- Thanks (thank you, merci)

You MUST NOT answer questions about:
- Celebrities
- Politics
- History
- Science
- General knowledge
- Any topic not related to airline travel

If the user asks something outside these topics:
Politely refuse and say you can help only with airline travel topics.

CONVERSATION HISTORY:
{format_history(state.get('history', []))}

USER MESSAGE:
"{user_text}"

RULES:
1. Be polite and professional
2. Keep answers short (2–3 sentences)
3. Express any cost in loyalty points only
4. Never change topic
5. If unclear, assume it is travel-related and try to help
6. If clearly not travel-related, refuse politely

YOUR RESPONSE:
"""

                
                response_text = mini_model.generate(
                    prompt,
                    max_tokens=200,
                    temp=0.7,
                    top_k=40,
                    top_p=0.92
                ).strip()
                
                # Nettoyer
                response_text = clean_response(response_text)
                
                print(f"✅ LLM (general): {response_text}")
                
            except Exception as e:
                print(f"❌ LLM error: {e}")
                response_text = "I'm here to chat! I can discuss various topics or help you with flight-related questions. What's on your mind?"
        else:
            response_text = "I'm an AI assistant here to help! I specialize in flight information, but I'm happy to chat about other topics too. What would you like to discuss?"
    
    # Fallback final
    if not response_text:
        response_text = "I'm here to help! Feel free to ask me about flights, seats, or anything else you'd like to discuss."
    
    # Construire résultat
    result = {
        "intent": entities.get("intent") or "general",
        "slots": entities,
        "response": response_text,
        "last_question": None,
        "is_airline_related": entities["is_airline_related"]
    }
    
    print(f"✅ Final output: {json.dumps(result, indent=2)}\n")
    return result


def clean_response(text: str) -> str:
    """Nettoie la réponse du LLM"""
    # Enlever les préfixes communs
    prefixes = [
        "YOUR RESPONSE:", "Assistant'S RESPONSE:", "Assistant:", 
        "Assistant:", "Response:", "RESPONSE:"
    ]
    
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    
    # Prendre seulement la première partie si double saut de ligne
    if "\n\n" in text:
        text = text.split("\n\n")[0]
    
    # Limiter à 5 phrases maximum
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) > 5:
        text = ' '.join(sentences[:5])
    
    return text.strip()


def format_history(history: list) -> str:
    """Formate l'historique pour le contexte"""
    if not history:
        return "(No previous conversation)"
    
    # Prendre les 3 derniers échanges
    recent = history[-3:]
    formatted = []
    
    for exchange in recent:
        if exchange.get('user'):
            formatted.append(f"User: {exchange['user']}")
        if exchange.get('assistant'):
            formatted.append(f"Assistant: {exchange['assistant']}")
    
    return '\n'.join(formatted)


def update_state(state: dict, llm_output: dict) -> dict:
    """Met à jour l'état de conversation"""
    # Ajouter entités
    if "slots" in llm_output and llm_output["slots"]:
        for k, v in llm_output["slots"].items():
            if v and k not in ["keywords", "cities"]:
                state[k] = v
    
    # Mettre à jour dernière question
    if "last_question" in llm_output:
        state["last_question"] = llm_output["last_question"]
    
    # Tier par défaut
    if "loyalty_tier" not in state:
        state["loyalty_tier"] = "star"
    
    # Historique
    if "history" not in state:
        state["history"] = []
    
    state["history"].append({
        "user": llm_output.get("user_input", ""),
        "assistant": llm_output.get("response", ""),
        "intent": llm_output.get("intent"),
        "is_airline": llm_output.get("is_airline_related", False)
    })
    
    # Limiter à 10 échanges
    if len(state["history"]) > 10:
        state["history"] = state["history"][-10:]
    
    return state


def build_prompt(user_text: str, state: dict) -> str:
    """Fonction legacy pour compatibilité"""
    return f"User: {user_text}\nState: {state}"