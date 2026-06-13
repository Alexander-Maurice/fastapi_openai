from data.names import names

def check_contacts_from_message(user_message):
    symbols = [',', '!', '-', '+', '.', '(', ')', '"']

    for symbol in symbols:
        while symbol in user_message:
            user_message = user_message.replace(symbol, '')
    message = user_message.split()
    name = None
    phone = None

    for elem in message:
        if elem in names:
            name = elem
        if check_phones(elem):
            phone = elem

    if name or phone:
        return (name, phone)
    else:
        return None


def check_phones(raw_phone):
    elements = ['+', '(', ')', '-', ',']
    for elem in elements:
        while elem in raw_phone:
            raw_phone = raw_phone.replace(elem, '')

    massive = raw_phone.split()
    result_massive = []
    for elem in massive:
        if elem not in elements:
            result_massive.append(elem)

    result_massive = ''.join(result_massive)
    return result_massive.isdigit()


def write_contact_to_txt(question):
    name, phone = check_contacts_from_message(question)
    with open('agents/phones.txt', 'a', encoding='utf-8') as f:
        f.write('\n')
        f.write('\n')
        f.write(f'Имя клиента: {name}')
        f.write('\n')
        f.write(f'Телефон: {phone}')
        f.write('\n')
        f.write('________________')


