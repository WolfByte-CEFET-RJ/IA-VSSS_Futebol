import os

# path/{file}_processed
def create_processed_folder(path):
    processed_path = os.path.join (os.path.dirname(path), f'{os.path.basename(path).split(".")[0]}_processed')
    if not os.path.exists(processed_path):
        print(f'Criando diretório {processed_path}')
        os.mkdir(processed_path)
    return processed_path