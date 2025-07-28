import streamlit as st
import random
import time

# --- Game Configuration ---
GAME_TITLE = "Mind Spark: The Ultimate Math Challenge 🧠"
TOTAL_OPERATIONS = 7
INITIAL_TIME_SECONDS = 30 # As per your requirement

# --- Session State Initialization ---
# This helps maintain game state across reruns of the script
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'current_operation_num' not in st.session_state:
    st.session_state.current_operation_num = 0
if 'current_answer' not in st.session_state:
    st.session_state.current_answer = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'high_score' not in st.session_state:
    st.session_state.high_score = 0 # High score for the current session/user
if 'feedback_message' not in st.session_state:
    st.session_state.feedback_message = ""
if 'feedback_color' not in st.session_state:
    st.session_state.feedback_color = "black"
if 'last_result' not in st.session_state: # To store the result of the previous operation
    st.session_state.last_result = None

# --- Utility Functions ---

def get_random_int(min_val, max_val):
    return random.randint(min_val, max_val)

def generate_operation(first_term, current_op_number):
    """
    Generates a random arithmetic operation (+, -, *, /) ensuring a positive integer result.
    The first_term is provided from the previous operation's result.
    Difficulty increases with current_op_number.
    """
    operators = ['+', '-', '*', '/']
    operator = random.choice(operators)
    
    # Adjust number ranges based on difficulty (operation number)
    # These max values guide num2 generation for addition/subtraction,
    # and also num1/num2 for multiplication/division
    max_operand_val = 10 + current_op_number * 3 # General max for operands
    max_multi_div_operand = 5 + current_op_number # Max for multiplication/division operands

    num1 = first_term # The first number is the result from the previous operation
    num2, result = 0, -1 # Initialize with invalid result

    attempts = 0
    # Ensure num1 is not too small for certain operations, especially division/subtraction
    if num1 < 1: # If previous result was 0, make num1 at least 1 for sensible ops
        num1 = get_random_int(1, 10) # Start fresh if previous result was 0 or negative (shouldn't be negative though)

    while not (isinstance(result, int) and result >= 0) and attempts < 200:
        attempts += 1
        
        # Select operator ensuring it's feasible with num1
        # For very small num1, some ops might be hard/impossible to make positive integer
        feasible_operators = []
        if num1 > 0: # Division requires num1 > 0
            feasible_operators.append('/')
            feasible_operators.append('*')
            feasible_operators.append('-') # Subtraction generally okay if num1 is large enough
        feasible_operators.append('+') # Addition is always feasible
        
        # If no feasible operators (e.g., num1 is very large but we need smaller results),
        # or if we are stuck, fallback to addition.
        if not feasible_operators or attempts > 100:
            operator = '+'
        else:
            operator = random.choice(list(set(operators) & set(feasible_operators))) # Choose from common and feasible

        if operator == '+':
            num2 = get_random_int(1, max_operand_val)
            result = num1 + num2
        
        elif operator == '-':
            # Ensure num2 is less than or equal to num1 for positive result
            num2 = get_random_int(1, num1) # num2 must be <= num1
            result = num1 - num2
        
        elif operator == '*':
            num2 = get_random_int(2, max_multi_div_operand)
            result = num1 * num2
        
        elif operator == '/':
            # Ensure num1 is a multiple of num2 and num2 is not 0
            num2_candidates = [i for i in range(2, max_multi_div_operand + 1) if num1 % i == 0]
            if not num2_candidates: # If no divisors found in range, try different operator or higher range
                # Try to pick a different operator or force addition as fallback
                operator = random.choice([op for op in operators if op != '/']) # Avoid division for this round
                continue # Re-attempt generation with new operator

            num2 = random.choice(num2_candidates)
            result = num1 // num2 # Integer division
        
        # Final check for validity before returning
        if isinstance(result, int) and result >= 0:
            break
        
        # If result is still invalid, loop and try again with new numbers/operator
        
    # If after all attempts, we still don't have a valid result (shouldn't happen with current logic, but safety)
    if not (isinstance(result, int) and result >= 0):
        # Last resort fallback: simple addition
        num1 = get_random_int(1, 10)
        num2 = get_random_int(1, 10)
        operator = '+'
        result = num1 + num2

    return f"{num1} {operator} {num2}", result

# --- Game State Management ---

def start_game_session():
    st.session_state.game_started = True
    st.session_state.current_operation_num = 0
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    st.session_state.feedback_message = ""
    st.session_state.feedback_color = "black"
    st.session_state.last_result = get_random_int(5, 20) # Initial first term for the very first operation
    next_operation()

def next_operation():
    st.session_state.current_operation_num += 1
    if st.session_state.current_operation_num > TOTAL_OPERATIONS:
        end_game_session(True) # All operations completed
        return

    # Pass the result of the previous operation as the first term for the new one
    question, answer = generate_operation(st.session_state.last_result, st.session_state.current_operation_num)
    
    st.session_state.operation_text = question
    st.session_state.current_answer = answer
    st.session_state.user_input = "" # Clear user input
    st.rerun() # Rerun to update the UI with new question

def check_answer():
    user_input_val = st.session_state.user_input
    if user_input_val is None or user_input_val == "":
        st.session_state.feedback_message = "Please enter a number."
        st.session_state.feedback_color = "orange"
        # No rerun here, let the user re-enter
        return

    try:
        user_answer = int(user_input_val)
        if user_answer == st.session_state.current_answer:
            st.session_state.score += 1
            st.session_state.feedback_message = "Correct! ✅"
            st.session_state.feedback_color = "green"
            # Update last_result for the next operation
            st.session_state.last_result = st.session_state.current_answer
            # Give a small delay for feedback visibility before next operation
            time.sleep(0.5) 
            next_operation() # Advance to next operation
        else:
            st.session_state.feedback_message = f"Incorrect. ❌ The answer was {st.session_state.current_answer}. Try again!"
            st.session_state.feedback_color = "red"
            st.session_state.user_input = "" # Clear incorrect input
            # No rerun here, let user try again immediately
    except ValueError:
        st.session_state.feedback_message = "Invalid input. Please enter an integer."
        st.session_state.feedback_color = "orange"
        st.session_state.user_input = "" # Clear invalid input
        st.rerun() # Rerun to update feedback

def end_game_session(completed_all_ops):
    st.session_state.game_started = False
    
    elapsed_time = time.time() - st.session_state.start_time
    time_left_at_end = INITIAL_TIME_SECONDS - elapsed_time

    if completed_all_ops:
        final_message = f"🎉 Congratulations! You solved all {TOTAL_OPERATIONS} operations in {elapsed_time:.1f} seconds!"
        final_color = "green"
    else:
        final_message = f"⏰ Time's up! You solved {st.session_state.score} out of {TOTAL_OPERATIONS} operations."
        final_color = "red"
    
    # Update high score if current score is higher
    if st.session_state.score > st.session_state.high_score:
        st.session_state.high_score = st.session_state.score
        final_message += "\n\n🏆 New High Score!"

    st.session_state.final_game_message = final_message
    st.session_state.final_game_color = final_color
    st.rerun() # Rerun to switch to end screen

# --- UI Layout ---

st.header(GAME_TITLE)
st.markdown("Test your mental math skills! Solve 7 operations in 30 seconds.")

# --- Game Screens ---

if not st.session_state.game_started:
    # --- Start Screen ---
    st.markdown("## Get Ready to Spark Your Mind! 🚀")
    st.write("Solve as many math problems as you can within the time limit. Results are always positive integers.")
    st.write(f"You'll face {TOTAL_OPERATIONS} operations in {INITIAL_TIME_SECONDS} seconds.")
    
    st.info(f"🏆 Current Session High Score: **{st.session_state.high_score}** correct answers!")

    if st.button("Start Challenge!", type="primary"):
        start_game_session()
else:
    # --- Game Screen ---
    current_time_left = max(0, INITIAL_TIME_SECONDS - int(time.time() - st.session_state.start_time))
    
    # Check if time is up, if so, end game
    if current_time_left <= 0:
        end_game_session(False)
        st.stop() # Stop further execution to prevent displaying game screen briefly after timeout

    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric(label="Operation", value=f"{st.session_state.current_operation_num} / {TOTAL_OPERATIONS}")
    with col2:
        # Create a progress bar for the timer
        time_progress = current_time_left / INITIAL_TIME_SECONDS
        st.progress(time_progress, text=f"Time Left: {current_time_left}s")

    st.markdown(f"## {st.session_state.operation_text}") # Display the operation question

    # Input field with key binding for Enter
    user_answer_input = st.text_input(
        "Your Answer:",
        key="user_input", # Use a key to link input to session state
        value=st.session_state.user_input, # Bind input value to session state
        on_change=check_answer, # Trigger check_answer on change (includes Enter press)
        help="Press Enter to submit your answer."
    )
    
    # Display feedback message
    st.markdown(f"<p style='color: {st.session_state.feedback_color}; font-weight: bold;'>{st.session_state.feedback_message}</p>", unsafe_allow_html=True)

    # Note: Explicit submit button might not be needed if on_change works for Enter
    # if st.button("Submit Answer", type="secondary"):
    #     check_answer()

    # Re-run the script every second to update the timer
    time.sleep(1)
    st.rerun() # This will cause the script to run again and update time/progress bar

# --- End Screen ---
if not st.session_state.game_started and st.session_state.current_operation_num > 0: # Only show end screen after a game has been played
    st.markdown(f"## {st.session_state.final_game_message}", unsafe_allow_html=True)
    st.write("Ready for another round?")
    if st.button("Play Again!", type="primary"):
        st.session_state.game_started = True # Set to true to trigger game start on next rerun
        start_game_session() # Reinitialize game state
        st.rerun() # Rerun to start the game


# --- Subtle Twitch Hint ---
TWITCH_CHANNEL_NAME = "YourAwesomeTwitchChannel" # <<-- IMPORTANT: REPLACE WITH YOUR TWITCH CHANNEL NAME!
TWITCH_URL = f"https://www.twitch.tv/{TWITCH_CHANNEL_NAME}"

st.sidebar.markdown("---")
st.sidebar.markdown(f"Developed with brain sparks. [Join my streams on Twitch! 🎮]({TWITCH_URL})")
st.markdown("---")
st.markdown(f"A mental challenge brought to you by an enthusiastic streamer. Catch me live on [Twitch: {TWITCH_CHANNEL_NAME}](<https://www.twitch.tv/{TWITCH_CHANNEL_NAME}>)! 🌟")