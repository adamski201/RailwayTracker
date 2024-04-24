from dotenv import load_dotenv

from extract import get_station_train_services_data, train_station_arrival_data, train_station_cancellation_data

if __name__ == "__main__":

    load_dotenv()

    paddington_train_services_list = get_station_train_services_data("PAD")

    paddington_arrivals = train_station_arrival_data(
        paddington_train_services_list)

    paddington_cancellations = train_station_cancellation_data(
        paddington_train_services_list)
