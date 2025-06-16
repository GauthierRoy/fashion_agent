def ask_user():
    """Asks the user for their clothing preferences and returns a dictionary with the answers."""
    print("Hello! I am your personal shopping advisor. Let's find the perfect clothing for you.")

    
    name = input("What is your name? ")
    age = input("What is your age? ")
    location = input("Where are you located? ")
    size = input("What is your clothing size? ")

    occasions = input("Is it for a specific occasion? ")
    preferences = input("Do you have any specific preferences (e.g., color, style)? ")
    budget = input("What is your budget? ")

    print(f"Great, I will start looking for that...")
    return {
        "name": name,
        "age": age,
        "location": location,
        "size": size,
        "occasions": occasions,
        "preferences": preferences,
        "budget": budget,
    }