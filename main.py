from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd

app = Flask(__name__)
api = Api(app)

data_arg = reqparse.RequestParser()
data_arg.add_argument("Arrival", type=str, help="Enter arrival")
data_arg.add_argument("Departure", type=str, help="Enter departure")
data_arg.add_argument("success", type=str, default="fail")


def to_time(x):
    return pd.to_datetime(x.strip(), format='%H:%M')


def update_sucess(df):
    df['success'] = 'fail'
    m = df[(((df['Departure'].apply(to_time) - df['Arrival'].apply(to_time)).dt.total_seconds() / 60) >= 180)].index
    df.loc[m[:20], 'success'] = "success"
    df['arrival_date'] = df['Arrival'].apply(to_time)
    df.sort_values(by='arrival_date', inplace=True)
    df.drop(['arrival_date'], axis=1, inplace=True)
    return df


class flights(Resource):
    def __init__(self):
        self.df = pd.read_csv('data.csv')
        self.df.columns = [x.strip() for x in self.df.columns]
        self.df = update_sucess(self.df)

    def get(self, ID):
        # find data from csv based on user input
        data_fount = self.df.loc[self.df['flight ID'] == ID].to_json(orient="records")
        # return data found in csv
        return jsonify({'message': data_fount})

    # POST request on the url will hit this function
    def post(self, ID):
        # data parser to parse data from url
        args = data_arg.parse_args()
        args['flight ID'] = ID
        # if ID is already present
        if (self.df['flight ID'] == ID).any():
            return jsonify({"message": 'ID already exist'})
        else:
            # Save data to csv
            self.df = self.df.append(args, ignore_index=True)
            if self.df['success'].value_counts()['success'] < 20:
                self.df=self.df = update_sucess(self.df)
            self.df.to_csv("data.csv", index=False)
            print(self.df, self.df.value_counts())
            return jsonify({"message": 'Done'})



api.add_resource(flights, '/<ID>')

if __name__ == '__main__':
    app.run(debug=True)


