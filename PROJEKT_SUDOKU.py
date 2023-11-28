import pygame
from dokusan import generators
import numpy as np
import time
import os
import sys


pygame.font.init()
pygame.mixer.init()


def generate():
    '''
    Funkcja generuje tablicę sudoku, zapisuje ją w tablicy,
    natępnie zmienia jej format na 9x9
    '''
    
    arr = np.array(list(str(generators.random_sudoku(avg_rank=50))))
    arr = arr.reshape(9, 9).astype(np.int64).tolist()
    
    return arr


def format_time(secs):

    sec = secs % 60
    minute = secs // 60
    hour = minute // 60

    time_format = " " + str(minute) + ":" + str(sec)
    return time_format


def redraw_windowdow(window, board, time, strikes):

    window.fill((236, 221, 207))
    '''
        Wypisz czas
    '''
    font = pygame.font.SysFont("cambria", 40)
    text = font.render("Czas: " + format_time(time), 1, (0, 0, 0))
    window.blit(text, (350, 550))
    '''
        Wypisz liczbę błędów
    '''
    text = font.render("Błędy: " + str(strikes), 1, (0, 0, 0))
    window.blit(text, (0, 550))
    '''
        Narysuj siatkę i tablicę sudoku
    '''
    board.draw()


def find_empty(board):
    '''
    Znajduje puste miejsce w tablicy sudoku
    board: częściowo wypełniona tablica
    zwraca: pozycje w tablicy, krotkę (rząd, kolumna),
    jeżeli nie znajdzie pustego miejsca zwraca None
    '''
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
            '''
                (rząd, kolumna)
            '''
    return None


def valid(bo, num, pos):
    '''
    Sprawdza czy proponowany ruch jest legalny
    board: dwu - wymiarowa lista cyfr od 1 do 9
    pos: pozycjaw tablicy, krotka (rząd, kolumna)
    num: proponowany ruch, int
    zwraca: True / False w zależności od legalności ruchu
    '''
    '''
        Sprawdzam rząd
    '''
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False
    '''
        Sprawdzam kolumne
    '''
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False
    '''
        Sprawdzam kwadrat
    '''
    box_x = pos[1] // 3
    box_y = pos[0] // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if bo[i][j] == num and (i, j) != pos:
                return False
    return True


class Square:
    rows = 9
    columns = 9

    def __init__(self, value, row, column, width, height):

        self.value = value
        self.temp = 0
        self.row = row
        self.column = column
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, window):

        font = pygame.font.SysFont("cambria", 40)
        gap = self.width / 9
        x = self.column * gap
        y = self.row * gap
        if self.temp != 0 and self.value == 0:
            text = font.render(str(self.temp), 1, (128, 128, 128))
            window.blit(text, (x + 5, y + 5))
        elif not(self.value == 0):
            text = font.render(str(self.value), 1, (0, 0, 0))
            window.blit(text, (x + (gap / 2 - text.get_width() / 2),
                        y + (gap / 2 - text.get_height() / 2)))
        if self.selected:
            pygame.draw.rect(window, (255, 0, 0), (x, y, gap, gap), 3)

    def draw_change(self, window, g=True):

        font = pygame.font.SysFont("cambria", 40)
        gap = self.width / 9
        x = self.column * gap
        y = self.row * gap
        pygame.draw.rect(window, (236, 221, 207), (x, y, gap, gap), 0)
        text = font.render(str(self.value), 1, (0, 0, 0))
        window.blit(text, (x + (gap / 2 - text.get_width() / 2),
                           y + (gap / 2 - text.get_height() / 2)))
        if g:
            pygame.draw.rect(window, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pygame.draw.rect(window, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


class Grid():

    board = generate()

    def __init__(self, rows, columns, width, height, window):

        self.rows = rows
        self.columns = columns
        self.squares = [[Square(self.board[i][j], i, j, width, height)
                         for j in range(columns)] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        self.update_model()
        self.selected = None
        self.window = window

    def update_model(self):
        self.model = [[self.squares[i][j].value for j in range(
            self.columns)] for i in range(self.rows)]

    def place(self, val):
        row, column = self.selected
        if self.squares[row][column].value == 0:
            self.squares[row][column].set(val)
            self.update_model()
            if valid(self.model, val, (row, column)) and self.solve():
                return True
            else:
                self.squares[row][column].set(0)
                self.squares[row][column].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):

        row, column = self.selected
        self.squares[row][column].set_temp(val)

    def draw(self):
        '''
            Rysuję linie siatki
        '''
        gap = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(self.window, (0, 0, 0),
                             (0, i * gap), (self.width, i * gap), thick)
            pygame.draw.line(self.window, (0, 0, 0),
                             (i * gap, 0), (i * gap, self.height), thick)
        '''
            Rysuję kwadraty
        '''
        for i in range(self.rows):
            for j in range(self.columns):
                self.squares[i][j].draw(self.window)

    def select(self, row, column):
        '''
            Resetuje pozostałe kwadraty
        '''
        for i in range(self.rows):
            for j in range(self.columns):
                self.squares[i][j].selected = False
        self.squares[row][column].selected = True
        self.selected = (row, column)

    def clear(self):

        row, column = self.selected
        if self.squares[row][column].value == 0:
            self.squares[row][column].set_temp(0)

    def click(self, pos):
        '''
        pos: pozycja
        zwraca: krotkę (rząd, kolumna)
        '''
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    def is_finished(self):
        '''
        Funkcja sprawdzająca czy zagadka jest rozwiązana
        '''
        for i in range(self.rows):
            for j in range(self.columns):
                if self.squares[i][j].value == 0:
                    return False
        return True

    def solve(self):
        '''
        Algorytm rozwiązujący sudoku za pomocą 'BackTrackingu'
        :zwraca: rozwiazanie
        POTRZEBNY DO WŁAŚCIWEGO DZIAŁANIA RĘCZNEGO ROZWIĄZYWANIA SUDOKU
        '''
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find
        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i
                if self.solve():
                    return True
                self.model[row][col] = 0
        return False

    def solve_gui(self):
        '''
        Algorytm rozwiązujący sudoku za pomocą 'BackTrackingu'
        '''
        self.update_model()
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, column = find
        for i in range(1, 10):

            if valid(self.model, i, (row, column)):
                self.model[row][column] = i
                self.squares[row][column].set(i)
                self.squares[row][column].draw_change(self.window, True)
                self.update_model()
                pygame.display.update()
                pygame.time.delay(100)
                if self.solve_gui():
                    return True
                self.model[row][column] = 0
                self.squares[row][column].set(0)
                self.update_model()
                self.squares[row][column].draw_change(self.window, False)
                pygame.display.update()
                pygame.time.delay(100)
        return False


def main():

    pygame.display.set_caption("Sudoku")
    path = os.path.join(sys.path[0]) + "\\OST.mp3"
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)
    window = pygame.display.set_mode((540, 600))
    path = os.path.join(sys.path[0]) + "\\sudoku.png"
    icon = pygame.image.load(path)
    pygame.display.set_icon(icon)
    run = True
    while run:
        window.fill((236, 221, 207))
        font = pygame.font.SysFont("cambria", 40)
        text = font.render("Kliknij aby rozpocząć...", 1, (0, 0, 0))
        window.blit(text, (85, 350))
        icon = pygame.transform.scale(icon, (256, 256))
        window.blit(icon, (150, 50))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False
            if event.type == pygame.QUIT:
                quit()
    board = Grid(9, 9, 540, 540, window)
    key = None
    run = True
    start = time.time()
    strikes = 0
    while run:

        play_time = round(time.time() - start)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_KP1:
                    key = 1
                if event.key == pygame.K_KP2:
                    key = 2
                if event.key == pygame.K_KP3:
                    key = 3
                if event.key == pygame.K_KP4:
                    key = 4
                if event.key == pygame.K_KP5:
                    key = 5
                if event.key == pygame.K_KP6:
                    key = 6
                if event.key == pygame.K_KP7:
                    key = 7
                if event.key == pygame.K_KP8:
                    key = 8
                if event.key == pygame.K_KP9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None
                if event.key == pygame.K_SPACE:
                    board.solve_gui()
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.squares[i][j].temp != 0:
                        if board.place(board.squares[i][j].temp):
                            print("Dobrze")
                        else:
                            print("Źle")
                            strikes += 1
                        key = None
                        if board.is_finished():
                            print("Koniec Gry")
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key is not None:
            board.sketch(key)
        redraw_windowdow(window, board, play_time, strikes)
        pygame.display.update()


main()
pygame.quit()
