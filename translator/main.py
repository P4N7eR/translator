import re
import os
import pandas as pd
import csv
import sqlite3

class Translator:
    def __init__(self, dictionary_db_file):
        self.dictionary_db_file = dictionary_db_file
        self.dictionary = {}
        self.translation_history = []
        self.load_dictionary_from_db()
    
    def export_to_excel(self, export_file):
        if not self.dictionary:
            print("Dictionary is empty.")
            return

        data = {'Word': [], 'Translation': []}
        for word, translations in self.dictionary.items():
            data['Word'].extend([word] * len(translations))
            data['Translation'].extend(translations)

        df = pd.DataFrame(data)
        try:
            df.to_excel(export_file, index=False)
            print(f"Dictionary exported to {export_file} successfully!")
        except IOError as e:
            raise ValueError(f"Failed to export dictionary to Excel: {e}")
            
    def load_dictionary_from_db(self):
        if not os.path.exists(self.dictionary_db_file):
            print("Dictionary database file does not exist.")
            return

        try:
            conn = sqlite3.connect(self.dictionary_db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT korean_word, russian_word FROM Dictionary")
            rows = cursor.fetchall()
            for row in rows:
                korean_word = row[0]
                russian_word = row[1]
                self.dictionary[korean_word] = russian_word
            conn.close()
        except sqlite3.Error as e:
            raise ValueError(f"Failed to load dictionary from database: {e}")

    def translate_word_to_russian(self, word):
        if word in self.dictionary:
            return self.dictionary[word]
        else:
            return "Translation not found."

    def translate_word_to_korean(self, word):
        for korean_word, russian_word in self.dictionary.items():
            if russian_word == word:
                return korean_word
        return "Translation not found."

    def translate_sentence_to_russian(self, sentence):
        words = sentence.split()
        translated_sentence = []
        for word in words:

            translations = self.translate_word_to_russian(word).split(", ")
            translated_sentence.extend(translations)
        return ' '.join(translated_sentence)

    def translate_sentence_to_korean(self, sentence):
        words = sentence.split()
        translated_sentence = []
        for word in words:
            translations = self.translate_word_to_korean(word)
            translated_sentence.append(translations)
        return ' '.join(translated_sentence)

    def print_all_words(self):
        if not self.dictionary:
            print("Dictionary is empty.")
        else:
            for word, translations in self.dictionary.items():
                print(f"{word}: {translations}")

    def clear_dictionary(self):
        self.dictionary = {}
        self.save_dictionary_to_db()
        print("Dictionary cleared successfully.")

    def word_exists(self, word):
        return word in self.dictionary.keys()

    def add_translation_to_history(self, translation):
        self.translation_history.append(translation)

    def print_translation_history(self):
        if not self.translation_history:
            print("Translation history is empty.")
        else:
            for translation in self.translation_history:
                print(translation)

    def save_translation_history(self):
        try:
            with open("translation_history.txt", "w") as file:
                for translation in self.translation_history:
                    file.write(translation + "\n")
        except IOError as e:
            raise ValueError(f"Failed to save translation history: {e}")

    def update_dictionary(self, korean_word, russian_word):
        self.dictionary[korean_word] = russian_word
        self.save_dictionary_to_db()
        print("Dictionary updated successfully!")

    def delete_translation(self, korean_word, russian_word):
        if korean_word in self.dictionary and self.dictionary[korean_word] == russian_word:
            del self.dictionary[korean_word]
            self.save_dictionary_to_db()
            print("Translation deleted successfully!")
        else:
            print("Translation not found in dictionary.")

    def save_dictionary_to_db(self):
        if not os.path.exists(self.dictionary_db_file):
            print("Dictionary database file does not exist.")
            return

        try:
            conn = sqlite3.connect(self.dictionary_db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Dictionary")
            for korean_word, russian_word in self.dictionary.items():
                cursor.execute("INSERT INTO Dictionary (korean_word, russian_word) VALUES (?, ?)",
                               (korean_word, russian_word))
                
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            raise ValueError(f"Failed to save dictionary to database: {e}")

def add_words_from_csv_to_db(csv_file, db_file):
    if not os.path.exists(csv_file):
        raise ValueError("Dictionary CSV file does not exist.")

    if not os.path.exists(db_file):
        raise ValueError("Dictionary database file does not exist.")

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)

            for row in csv_reader:
                korean_word = row[0].strip()
                russian_word = row[1].strip()

                query = "REPLACE INTO Dictionary (korean_word, russian_word) VALUES (?, ?)"
                cursor.execute(query, (korean_word, russian_word))

        conn.commit()
        conn.close()
    except (sqlite3.Error, IOError) as e:
        raise ValueError(f"Failed to add words from CSV to database: {e}")

def main():
    dictionary_db_file = "dictionary.db"
    csv_file = "dictionary.csv"

    if not os.path.exists(dictionary_db_file):
        raise ValueError("Dictionary database file does not exist.")

    if not os.path.exists(csv_file):
        raise ValueError("Dictionary CSV file does not exist.")

    translator = Translator(dictionary_db_file)
    add_words_from_csv_to_db(csv_file, dictionary_db_file)

    while True:
        print("-------------------------------------")
        print("Enter one of the following operations:")
        print("'kr' - translate from Korean to Russian")
        print("'rk' - translate from Russian to Korean")
        print("'m' - additional functions")
        print("'q' - quit")
        print("-------------------------------------")
        choice = input("Your choice: ")

        if choice.lower() == "q":
            translator.save_translation_history()
            break

        if choice.lower() == "kr":
            print("-------------------------------------")
            print("Enter one of the following operations:")
            print("'W' - translate a word")
            print("'S' - translate a sentence")
            print("'B' - go back to the main menu")
            print("-------------------------------------")

            choice_2 = input("Your choice: ")

            if choice_2.lower() == "w":
                word = input("Enter a word to translate from Korean to Russian: ")
                translations = translator.translate_word_to_russian(word)
                print(f"Translation: {translations}")
                translator.add_translation_to_history(f"{word}: {translations}")

            elif choice_2.lower() == "s":
                sentence = input("Enter a sentence to translate from Korean to Russian: ")
                translation = translator.translate_sentence_to_russian(sentence)
                print(f"Sentence translation: {translation}")
                translator.add_translation_to_history(f"{sentence}: {translation}")

            elif choice_2.lower() == "b":
                continue

        if choice.lower() == "rk":

            print("-------------------------------------")
            print("Enter one of the following operations:")
            print("'W' - translate a word")
            print("'S' - translate a sentence")
            print("'B' - go back to the main menu")
            print("-------------------------------------")

            choice_2 = input("Your choice: ")

            if choice_2.lower() == "w":
                word = input("Enter a word to translate from Russian to Korean: ")
                translations = translator.translate_word_to_korean(word)
                print(f"Translation: {translations}")
                translator.add_translation_to_history(f"{word}: {translations}")

            elif choice_2.lower() == "s":
                sentence = input("Enter a sentence to translate from Russian to Korean: ")
                translation = translator.translate_sentence_to_korean(sentence)
                print(f"Sentence translation: {translation}")
                translator.add_translation_to_history(f"{sentence}: {translation}")

            elif choice_2.lower() == "b":
                continue

        if choice.lower() == "m":
            print("-------------------------------------")
            print("Enter one of the following operations:")
            print("'a' - add a word")
            print("'d' - delete a translation")
            print("'u' - update a translation")
            print("'c' - clear the dictionary")
            print("'p' - print all words in the dictionary")
            print("'s' - select another dictionary file")
            print("'e' - export dictionary to Excel")
            print("'h' - print translation history")
            print("-------------------------------------")
            choice_2 = input("Your choice: ")

            if choice_2.lower() == "p":
                translator.print_all_words()

            elif choice_2.lower() == "a":
                word = input("Enter a word to add: ")
                translation = input("Enter a translation: ")
                translator.update_dictionary(word, translation)

            elif choice_2.lower() == "d":
                word = input("Enter a word to delete the translation: ")
                translation = input("Enter the translation to delete: ")
                translator.delete_translation(word, translation)

            elif choice_2.lower() == "u":
                word = input("Enter a word to update: ")
                translation = input("Enter the updated translation: ")
                translator.update_dictionary(word, translation)

            elif choice_2.lower() == "c":
                translator.clear_dictionary()

            elif choice_2.lower() == "s":
                db_file = input("Enter the path to the dictionary database file: ")
                if os.path.exists(db_file):
                    translator = Translator(db_file)
                else:
                    print("Dictionary database file does not exist.")

            elif choice_2.lower() == "e":
                export_file = input("Enter the name of the exported file: ")
                translator.export_to_excel(export_file)

            elif choice_2.lower() == "h":
                translator.print_translation_history()

            else:
                print("Invalid choice. Please try again.")

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
