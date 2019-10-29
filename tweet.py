#!flask/bin/python

from flask import Flask, jsonify, request
import tasks

app = Flask(__name__)

@app.route('/')
def analysis():
        # Retrieve the terms from user input
        terms = request.args.get('terms', '')
        # Convert the input into a list of strings
        terms = terms.split()
        print('\nThese terms we will be counting in the text:')
        for item in terms:
                print(item)
        print('\n')
        # Perform the analysis/counting
        result = tasks.total_counting.delay(terms)
        print('Performing the analysis...')
        # Wait until the analysis is complete
        result.wait()
        print('The results are ready')
        # Retrieving and returning the results
        result = result.get(timeout=1)
        print('Returning the results')
        return jsonify(result)

if __name__ == '__main__':
        app.run(debug=True)
