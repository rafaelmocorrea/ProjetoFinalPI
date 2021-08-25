import cv2
import numpy as np
import moviepy.editor as mp
import os
from tkinter import *
from tkinter import filedialog

'''
Metodo 1, usa a area dos contornos
'''
global diretorio
diretorio = os.getcwd()

def dinamiza(vet,fps,t,limite):
    frames = fps*t
    ret = []
    for i in vet:
        for a in range(i-frames,i+frames+1):
            if ((a not in vet) or a == i) and (a >= 0 and a <= limite and a not in ret):
                ret.append(a)
    return ret

def filename(nome_arq):
    for i in range(len(nome_arq)):
        if nome_arq[-1 - i] == '.':
            ind = len(nome_arq) + (-1-i)
            break
    return nome_arq[0:ind] + '_sum.mp4'

def filtra_frames(media, frames, indices,limiar): #filtra os frames de acordo a média do área dos frames
    for i in range(len(indices)):
        area = 0
        contornos,_ = cv2.findContours(frames[i],cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        max_array = []
        for a in contornos:
            max_array.append(cv2.contourArea(a))
        max_array = np.array(max_array)
        if max_array.max() < media*(limiar/100): #se não houver um objeto maior que a média ponderada com o limiar o frame é removido
            frames[i] = []
            indices[i] = -1

def sumarizador_frames(path,limiar=20): #retorna o índice e máscaras dos frames de interesse
    print("Sumarizador iniciado")
    bg = cv2.createBackgroundSubtractorMOG2()
    video = cv2.VideoCapture(path)
    conta_frame = 0

    area_contornos = []
    frames_conteudo = []
    num_frames_conteudo = []

    while(1):
        ret,frame = video.read()

        if ret == False:
            print("Acabou")
            break
        
        conta_frame += 1
        mask = bg.apply(frame)
        _,mask = cv2.threshold(mask,150,255,cv2.THRESH_BINARY)
        knl = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
        mask = cv2.erode(mask,knl,iterations=2)
        mask = cv2.dilate(mask,knl,iterations=2)
        contornos,_ = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        areas_aux = []
        if len(contornos) > 0:
            for a in contornos:
                areas_aux.append(cv2.contourArea(a))
            areas_aux = np.array(areas_aux)
            area_contornos.append(areas_aux.mean()) #media das areas do frame
            frames_conteudo.append(mask)
            num_frames_conteudo.append(conta_frame)
    area_contornos = [n for n in area_contornos if n != 0]
    area_contornos = np.array(area_contornos)

    if len(num_frames_conteudo) > 0:
        print("Filtrando Frames")
        filtra_frames(area_contornos.mean(),frames_conteudo,num_frames_conteudo,limiar)
    video.release()
    num_frames_conteudo = [a for a in num_frames_conteudo if a > -1]
    frames_conteudo = [b for b in frames_conteudo if len(b)>0]
    return num_frames_conteudo, conta_frame

def aplica_sumarizacao(path, indices,fps):
    video = cv2.VideoCapture(path)
    conta_frame = 0
    width = int(video.get(3))
    height = int(video.get(4))
    tam = (width,height)
    output = cv2.VideoWriter(filename(path),cv2.VideoWriter_fourcc(*'mp4v'),fps,tam)

    while(video.isOpened()):
        ret,frame = video.read()
        if ret == False:
            break
        conta_frame += 1
        if conta_frame in indices:
            output.write(frame)
        
    video.release()
    output.release()
    print(f'Arquivo salvo em {filename(path)}')

def fachada(arq,t,limiar):
    vid = mp.VideoFileClip(arq) #pega o fps do video
    fps = int(vid.fps)
    vid.close()
    frames_filtrados,limite = sumarizador_frames(arq,limiar)
    if t != 0:
        frames_dinamizados = dinamiza(frames_filtrados,fps,t,limite)
    else:
        frames_dinamizados = frames_filtrados
    aplica_sumarizacao(arq,frames_dinamizados,fps) 

class Programa():
    def __init__(self,master = None):
        global diretorio
        self.padrao = ("Arial","10")
        self.cont1 = Frame(master)
        self.cont1["pady"] = 5
        self.cont1.pack()

        self.cont2 = Frame(master)
        self.cont2["padx"] = 5
        self.cont2.pack()
        
        self.contSel = Frame(master)
        self.contSel["pady"] = 5
        self.contSel.pack()

        self.contLim = Frame(master)
        self.contLim["pady"] = 5
        self.contLim.pack()

        self.contbotao= Frame(master)
        self.contbotao["pady"] = 5
        self.contbotao.pack()

        self.titulo = Label(self.cont1,text="Sumarizador de Vídeo: Método 1")
        self.titulo["font"] = ("Arial","10","bold")
        self.titulo.pack()

        self.dirbot = Button(self.cont2,text="Selecionar Video",command=self.seldiretorio)
        self.dirbot["font"] = ("Arial","8")
        self.dirbot["width"] = 20
        self.dirbot.pack(side = LEFT)

        self.tlabel = Label(self.contSel,text="T:",font=self.padrao)
        self.tlabel.pack(side=LEFT)
        self.tvalue = Entry(self.contSel)
        self.tvalue["width"] = 5
        self.tvalue["font"] = self.padrao
        self.tvalue.pack(side=LEFT)

        self.llabel = Label(self.contLim,text="Limiar:",font=self.padrao)
        self.llabel.pack(side=LEFT)
        self.lvalue = Entry(self.contLim)
        self.lvalue["width"] = 5
        self.lvalue["font"] = self.padrao
        self.lvalue.pack(side=LEFT)

        self.botao = Button(self.contbotao)
        self.botao["text"] = "Executar"
        self.botao["font"] = ("Arial","8")
        self.botao["width"] = 10
        self.botao["command"] = self.apertaBotao
        self.botao.pack()

    def seldiretorio(self):
        global diretorio
        diretorio = filedialog.askopenfilename(initialdir=diretorio,title='Selecione o Video',filetypes=(("Arquivos Mp4",".mp4"),("Todos arquivos","*.*")))

    def apertaBotao(self):
        global diretorio
        t = self.tvalue.get()
        lim = self.lvalue.get()
        fachada(diretorio,int(t),int(lim))


root = Tk()
root.title("Sumarizador de videos")
Programa(root)
root.mainloop()