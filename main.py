from utils.set_bot_commands import set_default_commands
from loader import bot
import handlers
from telebot.custom_filters import StateFilter


if __name__ == "__main__":
    try:
        bot.add_custom_filter(StateFilter(bot))
        set_default_commands(bot)
        bot.polling(none_stop=True)
    except ConnectionError as e:
        print('Ошибка соединения: ', e)


res = [{'id': 537087, 'name': 'Azzurra Guest House', 'starrating': 0.0, 'address': 'Via Genova 30', 'distance': '0.5 miles', 'price': 30.55}, {'id': 572502, 'name': 'Hotel Beautiful', 'starrating': 1.0, 'address': 'Via Milazzo 14', 'distance': '1.1 miles', 'price': 30.81}, {'id': 1768189344, 'name': 'Rhome Sweet Rhome Suite', 'starrating': 0.0, 'address': None, 'distance': '1.2 miles', 'price': 42.88}, {'id': 495936, 'name': 'Dandi Domus', 'starrating': 0.0, 'address': 'Via Buonarroti 39', 'distance': '1.1 miles', 'price': 44.03}, {'id': 258699, 'name': 'Orange Hotel', 'starrating': 4.0, 'address': 'Via Crescenzio 86', 'distance': '1.3 miles', 'price': 49.4}, {'id': 450253, 'name': 'Hotel Marvi', 'starrating': 2.0, 'address': 'Viale Pietro della Valle, 13', 'distance': '1.0 mile', 'price': 49.77}, {'id': 295099, 'name': 'Palma Residence', 'starrating': 0.0, 'address': 'Via Varese 5', 'distance': '1.1 miles', 'price': 52.11}, {'id': 464493, 'name': 'SunMoon', 'starrating': 0.0, 'address': 'Via dei Mille, 41/A', 'distance': '1.1 miles', 'price': 52.11}, {'id': 281917, 'name': 'Ferrari', 'starrating': 2.0, 'address': 'Via Giovanni Amendola 95, 4th Floor', 'distance': '0.9 miles', 'price': 54.4}, {'id': 295098, 'name': 'Angelica', 'starrating': 0.0, 'address': 'Via dei Mille 41', 'distance': '1.1 miles', 'price': 54.46}, {'id': 319137, 'name': 'Prince Inn', 'starrating': 0.0, 'address': 'Via Principe Eugenio 15', 'distance': '1.3 miles', 'price': 54.46}, {'id': 1441769696, 'name': 'Ave popolo', 'starrating': 0.0, 'address': 'Piazza Vittorio Emanuele II 35', 'distance': '1.2 miles', 'price': 54.46}, {'id': 461932, 'name': 'Friendship Place', 'starrating': 0.0, 'address': 'Via dei Mille, 41/A', 'distance': '1.1 miles', 'price': 55.71}, {'id': 636091008, 'name': 'Rome Services Borgo Suites', 'starrating': 0.0, 'address': 'Borgo Vittorio, 85', 'distance': '1.2 miles', 'price': 56.71}, {'id': 1163704384, 'name': 'Gialli Vatican Guesthouse', 'starrating': 0.0, 'address': '183 Viale Giulio Cesare', 'distance': '1.5 miles', 'price': 58.63}, {'id': 199355, 'name': 'Hotel Scott House Rome', 'starrating': 3.0, 'address': 'Via Gioberti 30', 'distance': '0.9 miles', 'price': 58.99}, {'id': 1180512640, 'name': 'Nicolas Inn', 'starrating': 0.0, 'address': 'Via Cavour 295', 'distance': '0.6 miles', 'price': 59.11}, {'id': 287563, 'name': 'Eurorooms', 'starrating': 1.0, 'address': 'Via Palestro 87', 'distance': '1.2 miles', 'price': 60.06}, {'id': 571521, 'name': 'Hotel Leone', 'starrating': 1.0, 'address': 'Via Cavour, 47', 'distance': '0.8 miles', 'price': 60.1}, {'id': 556527, 'name': 'Raeli Hotel Lazio', 'starrating': 3.0, 'address': 'Via Vicenza, 8', 'distance': '1.0 mile', 'price': 61.79}, {'id': 292987, 'name': 'Hotel Chicago', 'starrating': 2.0, 'address': 'Via Gioberti 63', 'distance': '0.9 miles', 'price': 61.94}, {'id': 630008384, 'name': 'Dada Suites', 'starrating': 0.0, 'address': 'PIAZZA VITTORIO EMANUELE II 138', 'distance': '1.1 miles', 'price': 62.62}, {'id': 309386, 'name': 'Hotel Adriatic', 'starrating': 2.0, 'address': 'Via Vitelleschi 25', 'distance': '1.1 miles', 'price': 62.62}, {'id': 281502, 'name': 'Concorde', 'starrating': 2.0, 'address': 'Via Giovanni Amendola 95', 'distance': '0.8 miles', 'price': 62.78}, {'id': 284978, 'name': 'Magnifico Rome', 'starrating': 0.0, 'address': 'via Nazionale 243', 'distance': '0.6 miles', 'price': 62.89}]
