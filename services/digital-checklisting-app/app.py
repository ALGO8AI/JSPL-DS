from flask import Flask, request, jsonify

app = Flask(__name__)

def calculate_sum(items):
    return sum(next(iter(item.values())) for item in items)

def validate_input(data):
    if not isinstance(data, dict) or 'delays' not in data or 'Mainteinence' not in data:
        return False, "Input must contain 'delays' and 'Mainteinence'."
    if not isinstance(data['delays'], list) or not all(isinstance(d, dict) and len(d) == 1 for d in data['delays']):
        return False, "'delays' must be a list of single-key dictionaries."
    if not isinstance(data['Mainteinence'], list) or not all(isinstance(m, dict) and len(m) == 1 for m in data['Mainteinence']):
        return False, "'Mainteinence' must be a list of single-key dictionaries."
    return True, ""

@app.route('/calculate-preparation-time', methods=['POST'])
def calculate_preparation_time():
    input_data = request.get_json()
    is_valid, error_message = validate_input(input_data)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    total_delay = calculate_sum(input_data['delays'])
    total_maintenance = calculate_sum(input_data['Mainteinence'])
    preparation_time = max(total_delay, total_maintenance)

    return jsonify({"total preparation time": preparation_time})

if __name__ == '__main__':
    app.run(debug=True)
