import datetime
import sqlite3
import uuid
from uuid import uuid1
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import segno


class Check:
    count = 0

    # kontruktor
    def __init__(self):
        Check.count += 1
        self.count = Check.count
        self.size = 11
        self.font = 'Helvetica'
        self.page_width = 300
        self.page_height = 0
        self.biggest = 0
        self.can = canvas.Canvas(filename=f'check{self.count}.pdf', pagesize=(self.page_width, self.page_height))
        self.can.setFont(psfontname=self.font, size=self.size)
        try:
            self.con = sqlite3.connect('Back_472.db')
            self.cur = self.con.cursor()
        except Exception as e:
            raise Exception(f"Error DB: {e}")

        self.cashier = input('Ismingizni kiriting: ')
        self.uuid = f'{uuid1()}'
        self.inn = 307982389
        self.check_id = uuid.uuid1()
        self.date = datetime.datetime.today().strftime('%d-%m-%Y')
        self.time = datetime.datetime.now().time().strftime("%H:%M:%S")

    def _search_puchase(self):
        sql1_query = (f"""
                      SELECT
                         product, count, qqs, 
                         price, count * price,
                         count* price * qqs / 100 "
                         FROM Purchase
                         WHERE id={Check.count}""")
        datas = self.cur.execute(sql1_query).fetchall()
        return datas

    def data_qr_code(self):
        sql_query = f"""
        SELECT
            SUM(price * count),
            SUM(price * count * qqs / 100),
            SUM(price * count) * 0.01
        FROM Purchase
        WHERE id={Check.count};
        """
        data = self.cur.execute(sql_query).fetchone()
        return data

    def create_qr_code(self):
        data = self.data_qr_code()
        thank_you_text = 'Thank you for your Purchase!'
        text = (f"Check: #{Check.count} \n"
                f"INN:  {self.inn} \n"
                f"Date: {self.date} \n"
                f"Time: {self.time} \n"
                f"Check_id: {self.check_id} \n"
                f"Cashier: {self.cashier} \n"
                f"{len(thank_you_text) * '- '} \n"
                f"Total: {data[0]} \n"
                f"NDS: {data[1]} \n"
                f"Cashback: {data[2]} \n"
                f"{len(thank_you_text) * '_ '} \n"
                f"{thank_you_text}")
        qr_code = segno.make_qr(f'{data}' * 5)

        qr_code.save(f'qr_code{Check.count}.png')
        return qr_code.png_data_uri()

    def set_line(self):
        count = 0
        str_width = 0
        text = '_ '
        target = self.page_width - 20
        while target > str_width:
            count += 1
            str_width = self.can.stringWidth(text * count)
        x = (self.page_width - str_width) / 2
        y = self.page_height + 5
        self.can.drawString(x, y, text * count)

    def set_image(self, img):
        img_width, img_height = ImageReader(img).getSize()
        self.biggest = (self.page_width / img_width) / 2
        img_width = img_width * self.biggest
        img_height = img_height * self.biggest
        x = (self.page_width - img_width) / 2
        self.page_height += 10
        y = self.page_height
        self.can.drawImage(img, x, y, img_width, img_height)
        self.page_height += img_height + 10  # new

    def __index_pdf(self):
        """ Bu funksiya pdf ga ma'lumot yozadi."""
        # qr code
        self.set_image(self.create_qr_code())  # new

        for data in self._search_puchase():
            x = 10
            self.page_height += 30
            y = self.page_height - 15
            product = f'Product: {data[0]} '
            count = f'Count: {data[1]}x'
            qqs = f'NDS: {data[2]}%'
            price = f'{data[3]:,.2f}'
            count_price = f'{data[4]:,.2f}'
            qqs_price = f'{data[5]:,.2f}'
            
            self.can.drawString(x,y, product)
            self.can.drawRightString(self.page_width - 10,y, price)
            
            self.can.drawString(x, y - 15, count)
            self.can.drawRightString(self.page_width - 10, y - 15, count_price)

            self.can.drawString(x, y - 30, qqs)
            self.can.drawRightString(self.page_width - 10, y - 30, qqs_price)

            self.can.drawString(x, y, f'{data}')
            self.set_line()
            self.can.setPageSize((self.page_width, self.page_height))
        # logo
        self.set_image('logo.png')  # new
        # page size changed
        self.can.setPageSize((self.page_width, self.page_height))  # new

    def run(self):
        self.create_qr_code()
        self.__index_pdf()
        self.can.save()


if __name__ == '__main__':
    while True:
        con = input('continue?: ')
        if con in ['continue', 'con', 'c']:
            check = Check()
            check.run()
        else:
            break
