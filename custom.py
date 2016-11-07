mapping = {
    'The Weeknd - I Can`t Feel My Face (mp3)': 'files/weekend.mp3',
}

def get_notification_text(hash):
    return "Dear customer, thanks for the purchase. <p> You can download your file <a href='https://gateway.ipfs.io/ipfs/%s'>here</a>."  % hash

def get_error_text():
    return "Dear customer, you seem to have found an order without an associated file. Please email the store owner and ask for your purchase."
