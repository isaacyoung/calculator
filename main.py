#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('form.html')


@app.route('/calculator', methods=['POST'])
def calculator():
    result = ''
    hetong_jine = float(request.form['hetong_jine'])
    zhifu_fangshi = float(request.form['zhifu_fangshi'])
    qishu = int(request.form['qishu'])
    year_lilv = float(request.form['year_lilv'])
    shouqi_zujin_bilv = float(request.form['shouqi_zujin_bilv'])
    baozhengjin_bilv = float(request.form['baozhengjin_bilv'])
    guanlifei_bilv = float(request.form['guanlifei_bilv'])
    liugoujia = float(request.form['liugoujia'])
    gps = float(request.form['gps'])
    baoxianfei = float(request.form['baoxianfei'])
    xubao_baozhengjin = float(request.form['xubao_baozhengjin'])
    pinggufei = float(request.form['pinggufei'])
    tiqian = float(request.form['tiqian'])

    shiji_rongzi_jine = hetong_jine * (1 - shouqi_zujin_bilv / 100.0)
    result += format_value("实际融资价值", shiji_rongzi_jine)
    result += format_value("保证金", hetong_jine * baozhengjin_bilv / 100.0)
    result += format_value("管理费", hetong_jine * guanlifei_bilv / 100.0)
    shouqikuan = hetong_jine * (shouqi_zujin_bilv / 100.0 + baozhengjin_bilv / 100.0 + guanlifei_bilv / 100.0) + liugoujia \
                 + gps + baoxianfei + xubao_baozhengjin + pinggufei
    result += format_value("首期款", shouqikuan)

    result += '<table class="table">'
    result += get_tr_title('期数', '租金', '本金', '利息', '剩余本金')

    # 期末等额本息
    if zhifu_fangshi == 0:
        shengyu_benjin = shiji_rongzi_jine
        all_zujin = 0
        all_lixi = 0
        all_benjin = 0
        for i in range(1, qishu + 1):
            if tiqian != 0 and tiqian != qishu and tiqian == i:
                lixi = 30 / 100.0 * year_lilv / 12.0 / 100.0 * shiji_rongzi_jine * (qishu - tiqian)
                zujin = shengyu_benjin + lixi
                benjin = shengyu_benjin
            else:
                zujin = (((1 + year_lilv / 12.0 / 100.0) ** qishu) * (year_lilv / 12.0 / 100.0) * shiji_rongzi_jine) / (
                    (1 + year_lilv / 12.0 / 100.0) ** qishu - 1)
                benjin = ((1 + year_lilv / 12.0 / 100.0) ** (i - 1) * (year_lilv / 12.0 / 100.0) * shiji_rongzi_jine) / (
                    (1 + year_lilv / 12.0 / 100.0) ** qishu - 1)
                lixi = zujin - benjin
            shengyu_benjin -= benjin
            result += get_tr_content(i, zujin, benjin, lixi, shengyu_benjin)
            all_zujin += zujin
            all_lixi += lixi
            all_benjin += benjin
            if tiqian != 0 and tiqian != qishu and tiqian == i:
                break
        result += get_tr_content('合计', all_zujin, all_zujin - all_lixi, all_lixi, '-')

    # 期末等本等息
    if zhifu_fangshi == 1:
        all_lixi = shiji_rongzi_jine * year_lilv / 12.0 / 100.0 * qishu
        all_zujin = shiji_rongzi_jine + all_lixi
        shengyu_benjin = shiji_rongzi_jine
        for i in range(1, qishu + 1):
            if tiqian != 0 and tiqian != qishu and tiqian == i:
                lixi = 30 / 100.0 * year_lilv / 12.0 / 100.0 * shiji_rongzi_jine * (qishu - tiqian)
                zujin = shengyu_benjin + lixi
                benjin = shengyu_benjin
            else:
                zujin = all_zujin / qishu
                lixi = all_lixi / qishu
                benjin = zujin - lixi
            shengyu_benjin -= benjin
            result += get_tr_content(i, zujin, benjin, lixi, shengyu_benjin)
            if tiqian != 0 and tiqian != qishu and tiqian == i:
                break
        result += get_tr_content('合计', all_zujin, all_zujin - all_lixi, all_lixi, '-')

    # 期末减本减息
    if zhifu_fangshi == 2:
        if qishu % 6 > 0:
            benjin_cishu = qishu // 6 + 1
        else:
            benjin_cishu = qishu // 6

        benjin_qishu = []
        for i in range(1, benjin_cishu + 1):
            benjin_qishu.append(6 * i)

        temp_bili = 0
        shengyu_benjin = shiji_rongzi_jine

        all_zujin = 0
        all_lixi = 0
        all_benjin = 0
        for i in range(1, qishu + 1):
            if i == qishu:
                benjin_bili = 1 - temp_bili
            elif i in benjin_qishu:
                if i == 6:
                    benjin_bili = 0.15
                    temp_bili += benjin_bili
                elif 6 < i < qishu:
                    benjin_bili = 0.1
                    temp_bili += benjin_bili
            else:
                benjin_bili = 0

            if tiqian != 0 and tiqian != qishu and tiqian == i:
                lixi = 30 / 100.0 * year_lilv / 12.0 / 100.0 * shiji_rongzi_jine * (qishu - tiqian)
                zujin = shengyu_benjin + lixi
                benjin = shengyu_benjin
                shengyu_benjin -= benjin
            else:
                benjin = shiji_rongzi_jine * benjin_bili
                shengyu_benjin -= benjin
                lixi = shengyu_benjin * year_lilv / 12.0 / 100.0
                zujin = benjin + lixi

            result += get_tr_content(i, zujin, benjin, lixi, shengyu_benjin)
            all_zujin += zujin
            all_lixi += lixi
            all_benjin += benjin
            if tiqian != 0 and tiqian != qishu and tiqian == i:
                break
        result += get_tr_content('合计', all_zujin, all_zujin - all_lixi, all_lixi, '-')

    # 期末不等额还款
    if zhifu_fangshi == 3:
        pass

    result += '</table>'
    return result


def get_tr_title(d1, d2, d3, d4, d5):
    s = ''
    s += '<tr>'
    s += '<td>' + str(d1) + '</td>'
    s += '<td>' + str(d2) + '</td>'
    s += '<td>' + str(d3) + '</td>'
    s += '<td>' + str(d4) + '</td>'
    s += '<td>' + str(d5) + '</td>'
    s += '</tr>'
    return s


def get_tr_content(d1, d2, d3, d4, d5):
    s = ''
    s += '<tr>'

    s += '<td>' + format_str(d1) + '</td>'
    s += '<td>' + format_str(d2) + '</td>'
    s += '<td>' + format_str(d3) + '</td>'
    s += '<td>' + format_str(d4) + '</td>'
    s += '<td>' + format_str(d5) + '</td>'
    s += '</tr>'
    return s


def format_str(s):
    if isinstance(s, str):
        return s
    else:
        return str(float('%.2f' % s))


def format_value(s, v):
    return '<p>' + s + ' = ' + str(v) + '</p><br>'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8082)
