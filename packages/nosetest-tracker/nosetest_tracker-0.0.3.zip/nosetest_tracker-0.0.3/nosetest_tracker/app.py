from xml.dom import minidom
import datetime
import xlwt


def read_test_xml(file_name):
    return_list = []
    try:
        test_file = open(file_name, 'r')
        xmldoc = minidom.parse(test_file)
        test_file.close()
        testsuite = xmldoc.getElementsByTagName('testsuite')
        test_nr = testsuite[0].attributes['tests'].value
        error_nr = testsuite[0].attributes['errors'].value
        failure_nr = testsuite[0].attributes['failures'].value

        case_list = xmldoc.getElementsByTagName('testcase')
        total_time = 0
        for case in case_list:
            total_time += float(case.attributes['time'].value)
        now = datetime.datetime.now()
        return_list.append(test_nr)
        return_list.append(failure_nr)
        return_list.append(unicode(total_time))
        return_list.append(str(now.strftime("%Y-%m-%d %H:%M")))
    except Exception, e:
        print e

    return return_list


def write_result(test_result):
    with open("nosetest-tracker.log", "a") as f:
        idx = 0
        for item in test_result:
            f.write(item + ',')
            idx = idx + 1
        if idx > 0:
            f.write('\n')


def read_testlog():
    date = []
    tests = []
    errors = []
    failure = []
    times = []
    with open("nosetest-tracker.log") as f:
        for lines in f:
            a_list = lines.split(',')
            date.append(a_list[3])
            tests.append(a_list[0])
            failure.append(a_list[1])
            times.append(a_list[2])

    content_list = [
        tests,
        failure,
        times,
        date
    ]
    return content_list


def edit_csv(test_cont):
    titles = [
        'test_total',
        'test_failed',
        'time',
        'date'
    ]

    wb = xlwt.Workbook()
    ws = wb.add_sheet('index')
    for i, item in enumerate(titles):
        for j, cont in enumerate(test_cont[i]):
            ws.write(j + 1, i, cont)
        ws.write(0, i, item)
    wb.save('nosetest-tracker.xls')


if __name__ == "__main__":
    test_result = read_test_xml("test_output.xml")
    write_result(test_result)
    edit_csv(read_testlog())
