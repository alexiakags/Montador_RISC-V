def ler_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()
        linhas = [linha.replace(',', '') for linha in linhas]
    return linhas


def traduzir_registrador(registrador):
    registradores = {
        'x0': '00000',
        'x1': '00001',
        'x2': '00010',
        'x3': '00011',
        'x4': '00100',
        'x5': '00101',
        'x6': '00110',
        'x7': '00111',
        'x8': '01000',
        'x9': '01001',
        'x10': '01010',
        'x11': '01011',
        'x12': '01100',
        'x13': '01101',
        'x14': '01110',
        'x15': '01111',
        'x16': '10000',
        'x17': '10001',
        'x18': '10010',
        'x19': '10011',
        'x20': '10100',
        'x21': '10101',
        'x22': '10110',
        'x23': '10111',
        'x24': '11000',
        'x25': '11001',
        'x26': '11010',
        'x27': '11011',
        'x28': '11100',
        'x29': '11101',
        'x30': '11110',
        'x31': '11111',
    }

    if registrador in registradores:
        return registradores[registrador]
    else:
        print(f"Registrador '{registrador}' nao reconhecido. Usando 'x0' como padrao.")
        return '00000'  

def traduzir_imediato(imediato):
    if imediato.startswith('x'):  
        return '000000000000'  
    else:
        valor = int(imediato)
        return format(valor, '012b')

def traduzir_instrucao(instrucao):
    opcode_dict = {
        "lb": "0000011",
        "sb": "0100011",
        "add": "0110011",
        "and": "0110011",
        "ori": "0010011",
        "sll": "0010011",
        "bne": "1100011",
        "lh": "0000011",
        "sh": "0100011",
        "sub": "0110011",
        "or": "0110011",
        "andi": "0010011",
        "srl": "0010011",
        "beq": "1100011",
        "lw": "0000011",
        "sw": "0100011",
        "xor": "0110011",
        "addi": "0010011",
        "lui": "0110111",  # Adicionado p/o li
        "move": "pseudoinstrucao",
        "li": "pseudoinstrucao"
    }
    
    partes = instrucao.strip().split()  



    if len(partes) < 1:
        print(f"Instrucao invalida: {instrucao}")
        return ''

    opcode = ''
    binario = ''
    
    #(R, I ou S)
    if partes[0] in opcode_dict:
        opcode = opcode_dict[partes[0]]
        if opcode == "pseudoinstrucao":
            binario = traduzir_pseudo_instrucao(instrucao)
        else:
            binario += opcode + ' '

        if partes[0] in ['lw', 'sw', 'lb', 'sb', 'lh', 'sh']:
            if len(partes) != 4:
                print(f"Instrucao invalida: {instrucao}")
                return ''

            binario += traduzir_registrador(partes[3]) + ' '  
            binario += traduzir_registrador(partes[1]) + ' '  
            offset, rs1 = partes[2].split('(')  
            binario += traduzir_imediato(offset) + ' '  
            binario += traduzir_registrador(rs1[:-1])

        elif partes[0] in ['add', 'and', 'sub', 'or', 'xor', 'sll', 'srl', 'bne', 'beq']:
            if len(partes) != 4:
                print(f"Instrucao invalida: {instrucao}")
                return ''
            binario += traduzir_registrador(partes[1]) + ' '  
            binario += traduzir_registrador(partes[2]) + ' '  
            binario += traduzir_registrador(partes[3]) + ' '  

            if partes[0] == 'add' or partes[0] == 'sub' or partes[0] == 'or' or partes[0] == 'and' or partes[0] == 'xor':
                binario += '0000000' + ' '
                binario += '000' + ' '
            elif partes[0] == 'sll' or partes[0] == 'srl':
                binario += '0000000' + ' '
                binario += '001' + ' '
            elif partes[0] == 'bne' or partes[0] == 'beq':
                binario += '0000000' + ' '
                binario += '001' + ' '

        elif partes[0] in ['andi', 'ori', 'addi']:
            if len(partes) != 4:
                print(f"Instrucao invalida: {instrucao}")
                return ''
            binario += traduzir_registrador(partes[1]) + ' '  
            binario += traduzir_registrador(partes[2]) + ' '  
            
            if partes[0] == 'andi' or partes[0] == 'ori':
                binario += '111 '  
            else:
                binario += '000 ' 

            binario += traduzir_imediato(partes[3]) 

    return binario

def traduzir_pseudo_instrucao(instrucao):
    partes = instrucao.strip().split()
    
    if partes[0] == 'move':
        return traduzir_instrucao(f"xor {partes[1]}, {partes[2]}, {partes[2]}")
    
    elif partes[0] == 'li':
        imediato = int(partes[2])
        if imediato >= 0 and imediato <= 4095:

            return traduzir_instrucao(f"ori {partes[1]}, x0, {imediato}")
        else:
            parte_alta = (imediato >> 12) & 0xFFF  
            parte_baixa = imediato & 0xFFF  
            return traduzir_instrucao(f"lui {partes[1]}, {parte_alta}\n" +
                                      f"ori {partes[1]}, {partes[1]}, {parte_baixa}")

def traduzir_e_salvar_saida(instrucoes, modo_saida):
    saida = ''
    for instrucao in instrucoes:
        instrucao = instrucao.strip()
        if instrucao:
            binario = traduzir_instrucao(instrucao)
            if binario:
                saida += binario + '\n'

    if modo_saida == 'arquivo':
        with open('saida.txt', 'w') as arquivo_saida:
            arquivo_saida.write(saida)
    elif modo_saida == 'terminal':
        print(saida)

def main():
    nome_arquivo = input("Digite o nome do arquivo de entrada: ")
    modo_saida = input("Digite 'arquivo' para salvar em arquivo ou 'terminal' para exibir no terminal: ")

    instrucoes = ler_arquivo(nome_arquivo)
    traduzir_e_salvar_saida(instrucoes, modo_saida)

main()