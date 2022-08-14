import sqlite3
import logging
from logging import FileHandler
from collections import defaultdict
import matplotlib.pyplot as plt
import palettable
from utils import *
import os
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 解决图像中的“-”负号的乱码问题


def init():
    logging.basicConfig(
        format='%(levelname)s %(asctime)s - %(message)s',
        level=logging.DEBUG,
        handlers=[
            FileHandler(
                filename='result.log',
                mode='w',
                encoding='utf-8')])
    logger = logging.getLogger()

    conn = sqlite3.connect('字节跳动hc.db')
    c = conn.cursor()

    def mkdir(name: str):
        if not os.path.exists(name):
            os.mkdir(name)

    mkdir('job')
    mkdir('city')
    return logger, c, conn


def get_total_hc():
    sql = '''
    select sum(HC) from HC
    '''
    c.execute(sql)
    total_hc = c.fetchone()[0]
    return total_hc


# sqlite的字符串拼接是“||”
def calc_job(job: Job) -> int:
    cond_sql = get_job_condition_sql(job)
    job_sql = 'select sum(HC) from HC where %s' % cond_sql
    c.execute(job_sql, (*job.includes, *job.excludes))
    ans = c.fetchone()[0]
    return ans or 0


def get_cities():
    cursor = c.execute('select city from HC')
    return set([row[0] for row in cursor])


def calc_city(city: str) -> int:
    city_sql = '''
    select sum(HC) from HC where city like '%' || ? || '%'
    '''
    c.execute(city_sql, (city,))
    ans = c.fetchone()[0]
    return ans or 0


def calc_job_city(city: str, job: Job) -> int:
    cond_sql = get_job_condition_sql(job)
    sql = f'''
    select sum(HC) from HC where
        city like '%' || ? || '%' and
        {cond_sql}
    '''
    c.execute(sql, (city, *job.includes, *job.excludes))
    ans = c.fetchone()[0]
    return ans or 0


# 某个工种hc的各城市占比
def get_job_hc_ratio(job_city_hc, job_hc):
    global jobs, cities
    job_city_hc_dict = defaultdict(int, job_city_hc)
    job_hc_dict = defaultdict(int, job_hc)
    return {
        job.name: remove_zero_val(
            sort_by_value(
                [
                    (city,
                     round(job_city_hc_dict[f'{city}{job}'] / job_hc_dict[job.name] * 100, 2),
                     job_city_hc_dict[f'{city}{job}'])
                    for city in cities
                ]
            )) for job in jobs
    }


def analyse_job_hc_ratio(job_city_hc, job_hc):
    global jobs, cities
    job_hc_ratio = get_job_hc_ratio(job_city_hc, job_hc)
    logging.debug('某个工种hc的各城市占比 %s' % job_hc_ratio)

    def get_explode(data):
        ln = len(data)
        if ln <= 6:
            return [0] * ln
        return [0] * (ln - 2) + [0.4, 0.8]

    for job in jobs:
        data = [val[2] for val in job_hc_ratio[job.name]]
        labels = [val[0] for val in job_hc_ratio[job.name]]
        plt.pie(data,
                labels=labels,  # 设置饼图标签
                colors=palettable.cartocolors.qualitative.Bold_9.mpl_colors,  # 设置饼图颜色
                autopct=make_autopct(data),  # 饼图同时显示数值和占比
                explode=get_explode(data))
        title = f'{job}岗位hc的各城市占比'
        plt.title(title)
        plt.savefig(os.path.join('job', f'{title}.jpg'))
        plt.close()


# 某个城市hc的各工种占比
def get_city_hc_ratio(job_city_hc, city_hc):
    global jobs, cities
    job_city_hc_dict = defaultdict(int, job_city_hc)
    city_hc_dict = defaultdict(int, city_hc)
    return {
        city: remove_zero_val(
            sort_by_value(
                [
                    (job.name,
                     round(job_city_hc_dict[f'{city}{job}'] / city_hc_dict[city] * 100, 2),
                     job_city_hc_dict[f'{city}{job}'])
                    for job in jobs
                ]
            )) for city in cities
    }


def analyse_city_hc_ratio(job_city_hc, city_hc):
    global jobs, cities
    city_hc_ratio = get_city_hc_ratio(job_city_hc, city_hc)
    logging.debug('某个城市hc的各工种占比 %s' % city_hc_ratio)

    def get_explode(data):
        ln = len(data)
        if ln <= 6:
            return [0] * ln
        return [0] * (ln - 2) + [0.4, 0.8]

    for city in cities:
        data = [val[2] for val in city_hc_ratio[city]]
        labels = [val[0] for val in city_hc_ratio[city]]
        plt.pie(data,
                labels=labels,
                colors=palettable.cartocolors.qualitative.Bold_9.mpl_colors,
                autopct=make_autopct(data),
                explode=get_explode(data))
        title = f'{city}hc的各工种占比'
        plt.title(title)
        plt.savefig(os.path.join('city', f'{title}.jpg'))
        plt.close()


def job_avg_min_salary(job: Job) -> float:
    cond_sql = get_job_condition_sql(job)
    # 和cpp类似，要转浮点数
    sql = f'''
    select round(sum(HC * min_salary) * 1.0 / sum(HC), 3) from HC where {cond_sql}
    '''
    c.execute(sql, (*job.includes, *job.excludes))
    ans = c.fetchone()[0]
    return ans or 0


def job_avg_max_salary(job: Job) -> float:
    cond_sql = get_job_condition_sql(job)
    # 和cpp类似，要转浮点数
    sql = f'''
    select round(sum(HC * max_salary) * 1.0 / sum(HC), 3) from HC where {cond_sql}
    '''
    c.execute(sql, (*job.includes, *job.excludes))
    ans = c.fetchone()[0]
    return ans or 0


def city_avg_min_salary(city: str) -> float:
    # 和cpp类似，要转浮点数
    sql = '''
    select round(sum(HC * min_salary) * 1.0 / sum(HC), 3) from HC where city like '%' || ? || '%'
    '''
    c.execute(sql, (city,))
    ans = c.fetchone()[0]
    return ans or 0


def city_avg_max_salary(city: str) -> float:
    # 和cpp类似，要转浮点数
    sql = '''
    select round(sum(HC * max_salary) * 1.0 / sum(HC), 3) from HC where city like '%' || ? || '%'
    '''
    c.execute(sql, (city,))
    ans = c.fetchone()[0]
    return ans or 0


if __name__ == '__main__':
    try:
        logger, c, conn = init()

        total_hc = get_total_hc()
        logging.debug('总hc：%s' % total_hc)  # 总hc： 8215

        # 靠后的岗位名字是根据冷门城市（如：福州）所涉及的岗位补上的
        jobs = [
            Job('测试', ['测试工程师', '测试开发工程师'], ['渗透测试工程师', '硬件测试工程师']),
            Job('渗透测试', ['渗透测试工程师']), Job('硬件测试', ['硬件测试工程师']),
            Job('安全', ['安全'], ['内容安全', '安全策略产品经理', '安全产品运营', '安全运营专员']),
            Job('C++', ['C++']), Job('营销', ['营销']),
            Job('计算机视觉', ['计算机视觉']), Job('前端', ['前端开发']),
            Job('后端', ['后端开发']), Job('NLP', ['NLP']),
            Job('运维', ['运维']), Job('大数据', ['大数据']),
            Job('多媒体', ['多媒体']), Job('客户端', ['客户端开发'], ['C++客户端']),
            Job('机器学习公平性方向研究员', ['机器学习公平性方向研究员']),
            Job('内容质量管培生', ['内容质量管培生']),
            Job('大客户销售', ['大客户销售']),
            Job('内容监测管培生', ['内容监测管培生']),
            Job('商业安全基地管培生', ['商业安全基地管培生']),
            Job('数据标注管培生', ['数据标注管培生']),
            Job('结构研发', ['结构研发工程师']),
            Job('项目经理', ['项目经理']),
            Job('硬件开发', ['硬件开发工程师']),
        ]
        job_hc = sort_by_value([(job.name, calc_job(job)) for job in jobs])
        logging.debug('job_hc %s' % job_hc)

        cities = get_cities()  # 28个城市
        logging.debug('cities %s %s' % (len(cities), cities))
        city_hc = sort_by_value([(city, calc_city(city)) for city in cities])
        logging.debug('city_hc %s' % city_hc)

        job_city_hc = sort_by_value([(f'{city}{job}', calc_job_city(
            city, job)) for job in jobs for city in cities])
        job_city_hc = remove_zero_val(job_city_hc)
        logging.debug('job_city_hc %s %s' % (len(job_city_hc), job_city_hc))

        analyse_job_hc_ratio(job_city_hc, job_hc)

        analyse_city_hc_ratio(job_city_hc, city_hc)

        salary = sort_by_value(
            [(job.name, job_avg_min_salary(job)) for job in jobs])
        logging.debug('岗位最小平均薪资 %s' % salary)

        salary = sort_by_value(
            [(job.name, job_avg_max_salary(job)) for job in jobs])
        logging.debug('岗位最大平均薪资 %s' % salary)

        salary = sort_by_value(
            [(city, city_avg_min_salary(city)) for city in cities])
        logging.debug('城市最小平均薪资 %s' % salary)

        salary = sort_by_value(
            [(city, city_avg_max_salary(city)) for city in cities])
        logging.debug('城市最大平均薪资 %s' % salary)
    except Exception as e:
        logging.exception(e)
    finally:
        conn.commit()
        conn.close()
