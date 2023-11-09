from util.utils import work_with_user

if __name__ == '__main__':
    user_name = input('Введите ваше имя: ')
    message = f'{user_name}, вы используете программу для прогнозирования цен на продукты'
    print(message)

    # Запуск контекстного меню
    work_with_user()
