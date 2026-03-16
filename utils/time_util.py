"""时间工具模块
提供时间相关的辅助功能
"""
from datetime import datetime, timedelta
from typing import Optional, Union
import time


def get_current_timestamp() -> int:
    """获取当前时间戳（秒）"""
    return int(time.time())


def get_current_timestamp_ms() -> int:
    """获取当前时间戳（毫秒）"""
    return int(time.time() * 1000)


def get_current_datetime() -> datetime:
    """获取当前日期时间"""
    return datetime.now()


def format_datetime(dt: Optional[datetime] = None,
                    fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def parse_datetime(date_str: str,
                   fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析日期时间字符串"""
    return datetime.strptime(date_str, fmt)


def add_days(dt: datetime, days: int) -> datetime:
    """增加天数"""
    return dt + timedelta(days=days)


def add_hours(dt: datetime, hours: int) -> datetime:
    """增加小时"""
    return dt + timedelta(hours=hours)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """增加分钟"""
    return dt + timedelta(minutes=minutes)


def add_seconds(dt: datetime, seconds: int) -> datetime:
    """增加秒"""
    return dt + timedelta(seconds=seconds)


def get_date_range(start_date: datetime,
                   end_date: datetime,
                   step_days: int = 1) -> list:
    """获取日期范围列表"""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current = add_days(current, step_days)
    return dates


def is_today(dt: datetime) -> bool:
    """判断是否是今天"""
    return dt.date() == datetime.now().date()


def is_yesterday(dt: datetime) -> bool:
    """判断是否是昨天"""
    yesterday = datetime.now().date() - timedelta(days=1)
    return dt.date() == yesterday


def get_time_diff(dt1: datetime, dt2: datetime) -> timedelta:
    """获取时间差"""
    return dt2 - dt1


def get_time_diff_seconds(dt1: datetime, dt2: datetime) -> float:
    """获取时间差（秒）"""
    diff = get_time_diff(dt1, dt2)
    return diff.total_seconds()


def get_time_diff_minutes(dt1: datetime, dt2: datetime) -> float:
    """获取时间差（分钟）"""
    return get_time_diff_seconds(dt1, dt2) / 60


def get_time_diff_hours(dt1: datetime, dt2: datetime) -> float:
    """获取时间差（小时）"""
    return get_time_diff_minutes(dt1, dt2) / 60


def get_time_diff_days(dt1: datetime, dt2: datetime) -> float:
    """获取时间差（天）"""
    return get_time_diff_hours(dt1, dt2) / 24


def sleep(seconds: Union[int, float]) -> None:
    """休眠指定秒数"""
    time.sleep(seconds)


def get_weekday(dt: Optional[datetime] = None) -> int:
    """获取星期几（0=周一，6=周日）"""
    if dt is None:
        dt = datetime.now()
    return dt.weekday()


def get_weekday_name(dt: Optional[datetime] = None) -> str:
    """获取星期名称"""
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return weekdays[get_weekday(dt)]


def is_weekend(dt: Optional[datetime] = None) -> bool:
    """判断是否是周末"""
    return get_weekday(dt) >= 5


def get_start_of_day(dt: Optional[datetime] = None) -> datetime:
    """获取当天的开始时间"""
    if dt is None:
        dt = datetime.now()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_end_of_day(dt: Optional[datetime] = None) -> datetime:
    """获取当天的结束时间"""
    if dt is None:
        dt = datetime.now()
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)