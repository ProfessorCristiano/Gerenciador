# Importando as bibliotecas
import tkinter as tk
from tkinter import ttk
import time
import socket
import struct
import paramiko

# Configurações de cores e estilo
corpadrao = "#1a1a1a"  # Fundo preto
corcontraste = "#ffa500"  # Dourado
cordesabilitado = "#808080"  # Cinza
fonte = "Consolas"

# Variáveis globais
dominio_usuario = "adm"
dominio_senha = "1234"

# Estrutura de dados para computadores
computadores = {
    "Laboratorio-1": [
        {"nome": "LAB1MAQ01", "ip": "172.18.101.1", "mac": "64:1c:67:e3:04:39"},
        {"nome": "LAB1MAQ02", "ip": "172.18.101.2", "mac": "64:1c:67:e2:ca:ca"},
    ],
    "Laboratorio-2": [
        {"nome": "LAB2MAQ01", "ip": "172.18.102.1", "mac": "64:1c:67:e2:c2:42"},
        {"nome": "LAB2MAQ02", "ip": "172.18.102.2", "mac": "64:1c:67:e3:02:2e"},
        {"nome": "LAB2MAQ20", "ip": "172.18.102.20", "mac": "64:1c:67:e3:02:40"},
    ],

}

# Função para Wake-on-LAN
def wake_on_lan(macaddress):
    """Switches on remote computers using WOL."""
    if len(macaddress) == 12:
        pass
    elif len(macaddress) == 12 + 5:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, '')
    else:
        raise ValueError('Formato de endereço MAC incorreto')

    data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
    send_data = bytearray()
    for i in range(0, len(data), 2):
        send_data.extend(struct.pack('B', int(data[i: i + 2], 16)))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ('<broadcast>', 7))
    sock.sendto(send_data, ('255.255.255.255', 7))

# Função para exibir saída no widget Text
def mostrar_saida(text_widget, saida):
    text_widget.insert(tk.END, saida + "\n")
    text_widget.see(tk.END)

# Função para ligar computadores
def ligar_computador(checkboxes, text_widget):
    selecionados = [comp for comp, var in checkboxes.items() if var.get()]
    mostrar_saida(text_widget, f"Ligando os computadores: {selecionados}")
    for comp in selecionados:
        computador = next((pc for lab in computadores.values() for pc in lab if pc["nome"] == comp), None)
        if computador:
            wake_on_lan(computador["mac"])
            mostrar_saida(text_widget, f"Computador {comp} ligado")

# Função para desligar computadores
def desligar_computador(checkboxes, text_widget):
    selecionados = [comp for comp, var in checkboxes.items() if var.get()]
    mostrar_saida(text_widget, f"Desligando os computadores: {selecionados}")
    for comp in selecionados:
        mostrar_saida(text_widget, f"Desligando {comp}")
'''
def executar_comando(checkboxes, comando, text_widget):
    selecionados = [comp for comp, var in checkboxes.items() if var.get()]
    mostrar_saida(text_widget, f"Executando comando: {comando} nos computadores: {selecionados}")
    for comp in selecionados:
        computador = next((pc for lab in computadores.values() for pc in lab if pc["nome"] == comp), None)
        if computador:
            try:
                mostrar_saida(text_widget, f"Tentando conectar em {computador['ip']} como {dominio_usuario}")
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(computador["ip"], username=dominio_usuario, password=dominio_senha, timeout=5)
                mostrar_saida(text_widget, f"Conectado em {computador['ip']}")
                stdin, stdout, stderr = ssh.exec_command(comando)
                saida = stdout.read().decode('utf-8')
                erro = stderr.read().decode('utf-8')
                if saida:
                    mostrar_saida(text_widget, f"Saída de {comp}:\n{saida}")
                if erro:
                    mostrar_saida(text_widget, f"Erro em {comp}:\n{erro}")
                ssh.close()
            except Exception as e:
                mostrar_saida(text_widget, f"Falha ao executar comando em {comp} ({computador['ip']}): {e}")
'''
def executar_comando(self):
    selecionados = [comp for comp, var in self.checkboxes.items() if var.get()]
    print(f"Executando comando SSH nos computadores: {selecionados}")
    comando = "tasklist"  # Comando equivalente ao 'ps aux' no Windows

    for comp in selecionados:
        # Obter informações do computador
        computador = next((pc for lab in self.computadores.values() for pc in lab if pc["nome"] == comp), None)
        if not computador:
            print(f"Erro: Informações do computador {comp} não encontradas.")
            continue

        ip = computador["ip"]
        try:
            # Configurar a conexão SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=ip,
                username=self.dominio_usuario,
                password=self.dominio_senha,
                timeout=10
            )

            # Executar o comando
            print(f"Executando '{comando}' em {comp} ({ip})...")
            stdin, stdout, stderr = ssh.exec_command(comando)
            saida = stdout.read().decode("utf-8", errors="ignore")
            erros = stderr.read().decode("utf-8", errors="ignore")

            # Exibir os resultados
            print(f"Saída de {comp}:\n{saida}")
            if erros:
                print(f"Erros de {comp}:\n{erros}")

            ssh.close()
        except Exception as e:
            print(f"Erro ao conectar ou executar comando em {comp} ({ip}): {e}")


# Função para abrir uma nova janela para comando personalizado
def abrir_janela_comando(checkboxes, text_widget):
    def executar_comando_personalizado():
        comando = input_comando.get()
        executar_comando(checkboxes, comando, text_widget)
        janela.destroy()

    janela = tk.Toplevel()
    janela.title("Executar Comando Personalizado")
    janela.geometry("400x200")
    janela.configure(bg=corpadrao)

    tk.Label(janela, text="Digite o comando:", bg=corpadrao, fg=corcontraste, font=(fonte, 12)).pack(pady=10)
    input_comando = tk.Entry(janela, font=(fonte, 12), width=40)
    input_comando.pack(pady=10)

    tk.Button(janela, text="Executar", command=executar_comando_personalizado, bg=corcontraste, fg=corpadrao, font=(fonte, 12)).pack(pady=10)

# Classe principal para a interface gráfica
class GerenciadorEstacoes:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Estações de Trabalho")
        self.root.geometry("1240x800")
        self.root.configure(bg=corpadrao)

        # Dicionários para armazenar os estados das caixas de seleção
        self.checkboxes = {}
        self.categoria_vars = {}

        # Configuração da interface
        self._criar_interface()

    def _criar_interface(self):
        # Título
        self.title_label = tk.Label(self.root, text="Gerenciador de Estações de Trabalho", bg=corpadrao, fg=corcontraste, font=(fonte, 16))
        self.title_label.grid(row=0, column=0, columnspan=3, pady=10)
        # Configura o grid do root para responsividade
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)  # Botões pode ser menor
        self.root.grid_columnconfigure(2, weight=2)  # Saída pode ser maior


        # Frame principal
        self.frame1 = tk.Frame(self.root, bg=corpadrao, highlightbackground=corcontraste, highlightthickness=1, width=50, height=800)
        self.frame1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame1.grid_rowconfigure(1, weight=1)
        self.frame1.grid_columnconfigure(0, weight=1)

        # Frame para botões
        self.frame2 = tk.Frame(self.root, bg=corpadrao, highlightbackground=corcontraste, highlightthickness=1)
        self.frame2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Frame para saída de dados
        self.frame3 = tk.Frame(self.root, bg=corpadrao, highlightbackground=corcontraste, highlightthickness=1)
        self.frame3.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        self.frame3.grid_rowconfigure(1, weight=1)
        self.frame3.grid_columnconfigure(0, weight=1)

        #label de informações
        self.info_label = tk.Label(self.frame3, text="Saída de Dados:", bg=corpadrao, fg=corcontraste, font=(fonte, 12, "bold"))
        self.info_label.grid(row=0, column=0, pady=10)

        # Área de texto para saída de dados com barra de rolagem
        self.text_saida = tk.Text(self.frame3, bg=corpadrao, fg=corcontraste, font=(fonte, 12), wrap=tk.WORD, height=40, width=50, highlightbackground=corcontraste, highlightthickness=1)
        self.text_saida.grid(row=1, column=0, sticky="nsew", pady=5, padx=5)
        scrollbar = tk.Scrollbar(self.frame3, orient=tk.VERTICAL, command=self.text_saida.yview, width=18, bg=corpadrao, troughcolor=corpadrao, activebackground=corcontraste)
        self.text_saida.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", padx=5)

        # label para caixa de Seleção
        self.label_categoria = tk.Label(self.frame1, text="Selecione os computadores:", bg=corpadrao, fg=corcontraste, font=(fonte, 12, "bold"), width=50, anchor="w")
        self.label_categoria.grid(row=0, column=0, pady=10)

        # Frame interno para checkboxes com barra de rolagem
        self.frame_scroll = tk.Frame(self.frame1, bg=corpadrao,padx=5, pady=5, highlightbackground=corcontraste, highlightthickness=1,width=50, height=800)
        self.frame_scroll.grid(row=1, column=0, sticky="nsew", pady=5, padx=5)
        # Configuração do grid para o frame rolável
        self.frame_scroll.grid_rowconfigure(0, weight=1)
        self.frame_scroll.grid_columnconfigure(0, weight=1)
        
        # Criação do canvas e scrollbar
        self.canvas = tk.Canvas(self.frame_scroll, bg=corpadrao, highlightthickness=0, highlightbackground=corcontraste)
        self.scrollbar_check = tk.Scrollbar(self.frame_scroll, orient="vertical", command=self.canvas.yview, width=18, bg=corpadrao, troughcolor=corpadrao, activebackground=corcontraste)
        self.scrollable_frame = tk.Frame(self.canvas, bg=corpadrao)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_check.set)

        # Use linha 0 para canvas e scrollbar, sticky="nsew" para ambos
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_check.grid(row=0, column=1, sticky="ns", padx=5)

        # Garanta que o frame_scroll expanda corretamente
        self.frame_scroll.grid_rowconfigure(0, weight=1)
        self.frame_scroll.grid_columnconfigure(0, weight=1)


        # Criação das caixas de seleção dentro do frame rolável
        row = 0
        for lab, pcs in computadores.items():
            var_categoria = tk.BooleanVar()
            self.categoria_vars[lab] = var_categoria
            tk.Checkbutton(
                self.scrollable_frame,
                width=30,
                anchor="w",
                text=lab,
                variable=var_categoria,
                command=lambda lab=lab, var_categoria=var_categoria: self.selecionar_categoria(lab, var_categoria),
                bg=corpadrao,
                fg=corcontraste,
                selectcolor=corpadrao,
                font=(fonte, 12, "bold"),
                activebackground=corcontraste,
                activeforeground=corpadrao,
                highlightbackground=corcontraste, 
                highlightthickness=1,
                
            ).grid(row=row, column=0, sticky="w", pady=5, padx=5)
            row += 1

            # Adicionando checkboxes para cada computador
            for pc in pcs:
                var = tk.BooleanVar()
                self.checkboxes[pc["nome"]] = var
                tk.Checkbutton(
                    self.scrollable_frame,
                    width=50,
                    anchor="w",
                    text=f" -> {pc['nome']} - {pc['ip']} - {pc['mac']}  .",
                    variable=var,
                    bg=corpadrao,
                    fg=corcontraste,
                    selectcolor=corpadrao,
                    font=(fonte, 10),
                    activebackground=corcontraste,
                    activeforeground=corpadrao,
                    highlightbackground=corcontraste, 
                    highlightthickness=1
                    
                ).grid(row=row, column=0, sticky="w", padx=20, pady=2)
                row += 1


        # label para botões de ação
        self.label_acoes = tk.Label(self.frame2, text="Ações:", bg=corpadrao, fg=corcontraste, font=(fonte, 12, "bold"))
        self.label_acoes.grid(row=0, column=0, pady=10)

        # Botões de ação
        tk.Button(self.frame2, text="Ligar Computador", command=lambda: ligar_computador(self.checkboxes, self.text_saida), bg=corcontraste, fg=corpadrao, width=20, height=1, highlightbackground=corcontraste, highlightthickness=1, activebackground=corpadrao, activeforeground=corcontraste, font=(fonte, 12, "bold")).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        tk.Button(self.frame2, text="Desligar Computador", command=lambda: desligar_computador(self.checkboxes, self.text_saida), bg=corcontraste, fg=corpadrao, width=20, height=1, highlightbackground=corcontraste, highlightthickness=1, activebackground=corpadrao, activeforeground=corcontraste, font=(fonte, 12, "bold")).grid(row=2, column=0, pady=10, padx=10, sticky="w")
        tk.Button(self.frame2, text="Executar Tasklist", command=lambda: executar_comando(self.checkboxes, "tasklist", self.text_saida), bg=corcontraste, fg=corpadrao, width=20, height=1, highlightbackground=corcontraste, highlightthickness=1, activebackground=corpadrao, activeforeground=corcontraste, font=(fonte, 12, "bold")).grid(row=3, column=0, pady=10, padx=10, sticky="w")
        tk.Button(self.frame2, text="Comando Personalizado", command=lambda: abrir_janela_comando(self.checkboxes, self.text_saida), bg=corcontraste, fg=corpadrao, width=20, height=1, highlightbackground=corcontraste, highlightthickness=1, activebackground=corpadrao, activeforeground=corcontraste, font=(fonte, 12, "bold")).grid(row=4, column=0, pady=10, padx=10, sticky="w")

    def selecionar_categoria(self, categoria, var_categoria):
        for pc in computadores[categoria]:
            self.checkboxes[pc["nome"]].set(var_categoria.get())

# Inicialização da aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = GerenciadorEstacoes(root)
    root.mainloop()
