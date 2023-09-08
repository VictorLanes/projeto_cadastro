import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QListWidget, QListWidgetItem, QMessageBox
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Cadastro de Fornecedor'
        self.left = 100
        self.top = 100
        self.width = 400
        self.height = 400
        self.edit_mode = False
        self.data_loaded = False
        self.initUI()
        self.connect_to_database()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.label_razao_social = QLabel('RAZÃO SOCIAL:', self)
        self.label_razao_social.move(50, 50)

        self.textbox_razao_social = QLineEdit(self)
        self.textbox_razao_social.move(200, 50)
        self.textbox_razao_social.resize(150, 30)

        self.label_endereco = QLabel('ENDEREÇO:', self)
        self.label_endereco.move(50, 90)

        self.textbox_endereco = QLineEdit(self)
        self.textbox_endereco.move(200, 90)
        self.textbox_endereco.resize(150, 30)

        self.label_contato = QLabel('CONTATO:', self)
        self.label_contato.move(50, 130)

        self.textbox_contato = QLineEdit(self)
        self.textbox_contato.move(200, 130)
        self.textbox_contato.resize(150, 30)

        self.button_save = QPushButton('Salvar', self)
        self.button_save.move(50, 170)
        self.button_save.clicked.connect(self.save_to_database)

        self.button_edit = QPushButton('Editar', self)
        self.button_edit.move(150, 170)
        self.button_edit.clicked.connect(self.toggle_edit_mode)

        self.button_delete = QPushButton('Excluir', self)
        self.button_delete.move(250, 170)
        self.button_delete.clicked.connect(self.delete_from_database)

        self.button_print = QPushButton('Imprimir', self)
        self.button_print.move(50, 330)
        self.button_print.clicked.connect(self.save_to_pdf)

        self.button_list = QPushButton('Listar Fornecedores', self)
        self.button_list.move(200, 330)
        self.button_list.clicked.connect(self.list_fornecedores)

        self.button_back = QPushButton('Voltar', self)
        self.button_back.move(300, 330)
        self.button_back.clicked.connect(self.hide_list)

        self.list_widget = QListWidget(self)
        self.list_widget.setGeometry(50, 210, 300, 100)
        self.list_widget.itemClicked.connect(self.select_item)

    def connect_to_database(self):
        try:
            self.conn = mysql.connector.connect(
                host='127.0.0.1',
                database='teste',
                user='root',
                password='W44n3sz99@',
            )
            self.cursor = self.conn.cursor()

            create_table_query = """
            CREATE TABLE IF NOT EXISTS fornecedor (
                id INT AUTO_INCREMENT PRIMARY KEY,
                razao_social VARCHAR(255) NOT NULL,
                endereco VARCHAR(255),  -- Correção: Adicionei o campo de endereço
                contato VARCHAR(255)
            )
            """
            self.cursor.execute(create_table_query)
            self.conn.commit()

            print("Conexão com o banco de dados estabelecida.")
        except Exception as e:
            print(f"Erro na conexão com o banco de dados: {str(e)}")

    def save_to_database(self):
        razao_social = self.textbox_razao_social.text()
        endereco = self.textbox_endereco.text()
        contato = self.textbox_contato.text()

        if self.edit_mode:
            try:
                selected_item = self.list_widget.currentItem()
                if selected_item is not None:
                    selected_id = selected_item.data(1)
                    query = "UPDATE fornecedor SET razao_social = %s, endereco = %s, contato = %s WHERE id = %s"
                    self.cursor.execute(query, (razao_social, endereco, contato, selected_id))
                    self.conn.commit()
                    print('Dados do fornecedor atualizados.')
                    self.toggle_edit_mode()
                    self.clear_fields()
                    self.load_data()
                else:
                    QMessageBox.warning(self, 'Aviso', 'Selecione um fornecedor para editar.')
            except Exception as e:
                print(f"Erro ao atualizar dados no banco de dados: {str(e)}")
        else:
            try:
                query = "INSERT INTO fornecedor (razao_social, endereco, contato) VALUES (%s, %s, %s)"
                self.cursor.execute(query, (razao_social, endereco, contato))
                self.conn.commit()
                print('Fornecedor cadastrado no banco de dados.')
                self.clear_fields()
                if self.data_loaded:  # Verifica se os dados já foram carregados
                    self.load_data()  # Recarrega os dados após salvar
            except Exception as e:
                print(f"Erro ao inserir dados no banco de dados: {str(e)}")

    def toggle_edit_mode(self):
        if self.edit_mode:
            self.edit_mode = False
            self.button_edit.setText('Editar')
        else:
            self.edit_mode = True
            self.button_edit.setText('Cancelar Edição')

    def select_item(self, item):
        if self.edit_mode:
            item_id = item.data(1)
            try:
                query = "SELECT * FROM fornecedor WHERE id = %s"
                self.cursor.execute(query, (item_id,))
                result = self.cursor.fetchone()
                if result:
                    self.textbox_razao_social.setText(result[1])
                    self.textbox_endereco.setText(result[2])
                    self.textbox_contato.setText(result[3])
            except Exception as e:
                print(f"Erro ao buscar dados do fornecedor: {str(e)}")

    def clear_fields(self):
        self.textbox_razao_social.clear()
        self.textbox_endereco.clear()
        self.textbox_contato.clear()

    def delete_from_database(self):
        selected_item = self.list_widget.currentItem()
        if selected_item is not None:
            selected_id = selected_item.data(1)
            try:
                confirm = QMessageBox.question(self, 'Confirmar Exclusão', 'Tem certeza de que deseja excluir este fornecedor?', QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    query = "DELETE FROM fornecedor WHERE id = %s"
                    self.cursor.execute(query, (selected_id,))
                    self.conn.commit()
                    self.load_data()  # Recarrega a lista após a exclusão
                    self.clear_fields()
                    print('Fornecedor excluído do banco de dados.')
            except Exception as e:
                print(f"Erro ao excluir fornecedor do banco de dados: {str(e)}")

    def list_fornecedores(self):
        if not self.data_loaded:  # Verifica se os dados já foram carregados
            self.load_data()
            self.data_loaded = True  # Define a variável como True para evitar recarregar automaticamente

    def hide_list(self):
        self.list_widget.clear()
        self.data_loaded = False

    def load_data(self):
        try:
            query = "SELECT * FROM fornecedor"
            self.cursor.execute(query)
            fornecedores = self.cursor.fetchall()
            self.list_widget.clear()
            for fornecedor in fornecedores:
                item = QListWidgetItem(f"{fornecedor[1]} | {fornecedor[2]} | {fornecedor[3]}")
                item.setData(1, fornecedor[0])
                self.list_widget.addItem(item)
        except Exception as e:
            print(f"Erro ao buscar dados no banco de dados: {str(e)}")

    def save_to_pdf(self):
        try:
            query = "SELECT * FROM fornecedor"
            self.cursor.execute(query)
            fornecedores = self.cursor.fetchall()

            pdf_filename, _ = QFileDialog.getSaveFileName(self, 'Salvar em PDF', '', 'PDF Files (*.pdf)')
            if pdf_filename:
                c = canvas.Canvas(pdf_filename, pagesize=letter)
                c.drawString(100, 750, 'Fornecedores:')
                y = 730
                for fornecedor in fornecedores:
                    c.drawString(100, y, f"RAZÃO SOCIAL: {fornecedor[1]}")
                    c.drawString(150, y - 10, f"ENDEREÇO: {fornecedor[2]}")
                    c.drawString(150, y - 20, f"CONTATO: {fornecedor[3]}")
                    y -= 30
                c.save()
                print(f'PDF salvo como {pdf_filename}')
        except Exception as e:
            print(f"Erro ao criar o PDF: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
