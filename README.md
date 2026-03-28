# **Сценарий 1: Безопасность — Изоляция гостевой сети**
## Полная документация по выполнению

> **Проект:** Умная маршрутизация для офиса АгроТех  
> **Сценарий:** Безопасность  
> **Технологии:** ONOS, Mininet, OpenFlow 1.3, Python, Docker

---

## **Содержание**

1. [Описание сценария](#1-описание-сценария)
2. [Архитектура решения](#2-архитектура-решения)
3. [Установка и настройка](#3-установка-и-настройка)
4. [Файлы проекта](#4-файлы-проекта)
5. [Пошаговое выполнение](#5-пошаговое-выполнение)
6. [Демонстрация результата](#6-демонстрация-результата)
7. [Презентация](#7-презентация)
8. [Пояснения к скриншотам](#8-пояснения-к-скриншотам)

---

## 1. **Описание сценария**

### 1.1. Задача

Реализовать политику **«изоляция гостевой сети»** для корпоративной сети офиса:

| Требование | Описание |
|------------|----------|
| 🎯 **Цель** | Гостевой WiFi не должен иметь доступ к рабочим ресурсам компании |
| 🔐 **Безопасность** | Изоляция на уровне сети, без зависимости от настроек клиентов |
| ⚡ **Гибкость** | Политика применяется программно через SDN-контроллер |
| 🔄 **Масштабируемость** | Решение работает на любом количестве устройств |

### 1.2. Что реализовано

```
✅ Две изолированные подсети:
   • Рабочая: 10.0.1.0/24 (хосты h1, h2)
   • Гостевая: 10.0.2.0/24 (хосты h3, h4)

✅ Политика безопасности:
   • Внутри подсетей: связь разрешена ✅
   • Между подсетями: связь заблокирована ❌

✅ Управление через SDN:
   • Контроллер: ONOS 2.7.0
   • Протокол: OpenFlow 1.3
   • Интерфейс: REST API + Karaf CLI
```

---

## 2. **Архитектура решения**

### 2.1. Схема инфраструктуры

```
┌─────────────────────────────────────────────────────────┐
│                    Control Plane                         │
│  ┌─────────────────┐                                    │
│  │   ONOS 2.7.0    │  ← SDN-контроллер                  │
│  │   (Docker)      │  • Порт 6653: OpenFlow            │
│  │                 │  • Порт 8181: REST API/Web UI     │
│  │                 │  • Порт 8101: Karaf CLI           │
│  └────────┬────────┘                                    │
│           │ OpenFlow 1.3                                │
└───────────┼─────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────┐
│                    Data Plane                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Mininet + OVS                      │   │
│  │                                                 │   │
│  │  ┌─────┐                                       │   │
│  │  │  s1 │  ← Программный коммутатор            │   │
│  │  └──┬──┘                                       │   │
│  │     │                                          │   │
│  │  ┌──┴──┬──┬──┬──┐                             │   │
│  │  │  │  │  │  │  │                             │   │
│  │ [h1][h2][h3][h4] ← Хосты                      │   │
│  │  │  │  │  │  │  │                             │   │
│  │  ▼  ▼  ▼  ▼  ▼  ▼                             │   │
│  │10.0.1.1 10.0.1.2 10.0.2.1 10.0.2.2          │   │
│  │  │  │  │  │                                   │   │
│  │  ▼  ▼  ▼  ▼                                   │   │
│  │ [Рабочая сеть] [Гостевая сеть]               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.2. Таблица адресации

| Хост | Подсеть | IP-адрес | Назначение |
|------|---------|----------|------------|
| **h1** | Рабочая (10.0.1.0/24) | 10.0.1.1 | Рабочая станция 1 |
| **h2** | Рабочая (10.0.1.0/24) | 10.0.1.2 | Рабочая станция 2 |
| **h3** | Гостевая (10.0.2.0/24) | 10.0.2.1 | Гостевой доступ 1 |
| **h4** | Гостевая (10.0.2.0/24) | 10.0.2.2 | Гостевой доступ 2 |
| **s1** | — | — | Коммутатор (управляется ONOS) |

### 2.3. Политика безопасности

```
┌─────────────────────────────────────┐
│        Правила маршрутизации        │
├─────────────────────────────────────┤
│                                     │
│  ✅ РАЗРЕШЕНО:                      │
│  • h1 ↔ h2  (внутри Рабочей)       │
│  • h3 ↔ h4  (внутри Гостевой)      │
│                                     │
│  ❌ ЗАБЛОКИРОВАНО:                  │
│  • h3 → h1  (Гость → Работа)       │
│  • h3 → h2  (Гость → Работа)       │
│  • h4 → h1  (Гость → Работа)       │
│  • h4 → h2  (Гость → Работа)       │
│                                     │
└─────────────────────────────────────┘
```

---

## 3. **Установка и настройка**

### 3.1. Требования

| Компонент | Версия | Примечание |
|-----------|--------|------------|
| **ОС** | Ubuntu 20.04+ | VM или физическая машина |
| **Docker** | 20.10+ | Для запуска ONOS |
| **Python** | 3.8+ | Для скриптов топологии |
| **Mininet** | 2.3.0+ | Эмулятор сети |
| **OVS** | 2.13.8+ | Программный коммутатор |

### 3.2. Установка Docker

```bash
# Обновить пакеты
sudo apt-get update

# Установить Docker
sudo apt-get install -y docker.io

# Проверить установку
docker --version

# Добавить пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER
# После этого нужно перезайти в систему
```

### 3.3. Запуск ONOS

```bash
# Запустить ONOS в Docker
sudo docker run --name onos --rm \
  -p 6653:6653 -p 8181:8181 -p 8101:8101 \
  -d onosproject/onos

# Проверить что контейнер запущен
sudo docker ps

# Ожидаемый вывод:
# CONTAINER ID   IMAGE              STATUS   PORTS
# xxxxxxx        onosproject/onos   Up       0.0.0.0:6653->6653/tcp, ...
```

### 3.4. Настройка сети (если есть проблемы с IPv6)

```bash
# Отключить IPv6 в системе (если Docker не может скачать образ)
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1

# Настроить Docker использовать только IPv4
sudo mkdir -p /etc/docker
echo '{"dns": ["8.8.8.8", "8.8.4.4"], "ipv6": false}' | sudo tee /etc/docker/daemon.json

# Перезапустить Docker
sudo systemctl restart docker
```

### 3.5. Проверка ONOS

```bash
# Открыть веб-интерфейс в браузере:
# http://<IP-VM>:8181/onos/ui
# Логин: onos / Пароль: rocks

# Или проверить через API:
curl -u onos:rocks http://localhost:8181/onos/v1/devices
```

---

## 4. **Файлы проекта**

### 4.1. Структура репозитория

```
SDN_controller/
└── scenario_1/
    ├── topology.py        # Скрипт создания топологии Mininet
    ├── security_policy.py # Скрипт применения политики через REST API
    └── README.md          # Эта документация

```

### 4.2. topology.py — Создание топологии

```python
#!/usr/bin/env python3
"""Создание топологии с двумя подсетями и подключением к ONOS"""

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

def create_topology():
    net = Mininet(controller=None, switch=OVSSwitch)

    # Подключение к ONOS (указать реальный IP VM)
    c0 = net.addController('c0',
                            controller=RemoteController,
                            ip='10.24.13.143',  # IP вашей виртуальной машины
                            port=6653)

    # Коммутатор с OpenFlow 1.3
    s1 = net.addSwitch('s1', protocols='OpenFlow13')

    # Рабочая сеть
    h1 = net.addHost('h1', ip='10.0.1.1/24')
    h2 = net.addHost('h2', ip='10.0.1.2/24')

    # Гостевая сеть
    h3 = net.addHost('h3', ip='10.0.2.1/24')
    h4 = net.addHost('h4', ip='10.0.2.2/24')

    # Подключить хосты к коммутатору
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)

    # Запустить сеть
    net.build()
    c0.start()
    s1.start([c0])
    net.start()

    print("=== Topology started ===")
    print("Work net:  h1=10.0.1.1, h2=10.0.1.2")
    print("Guest net: h3=10.0.2.1, h4=10.0.2.2")

    CLI(net)  # Интерактивная консоль
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()
```

### 4.3. security_policy.py — Применение политики

```python
#!/usr/bin/env python3
"""Применение политики изоляции через REST API ONOS"""

import requests
import json

ONOS_IP = "localhost"
ONOS_PORT = 8181
BASE_URL = f"http://{ONOS_IP}:{ONOS_PORT}/onos/v1"
AUTH = ("onos", "rocks")  # Логин/пароль ONOS по умолчанию
HEADERS = {"Content-Type": "application/json"}

def get_device_id():
    """Получить ID коммутатора из ONOS"""
    resp = requests.get(f"{BASE_URL}/devices", auth=AUTH)
    devices = resp.json()["devices"]
    if not devices:
        print("Switches not found! Run Mininet first.")
        return None
    device_id = devices[0]["id"]
    print(f"Switch found: {device_id}")
    return device_id

def add_flow_rule(device_id, priority, src_ip, dst_ip, action="DROP"):
    """Добавить правило блокировки трафика"""
    # Для DROP оставляем treatment пустым
    instructions = [] if action == "DROP" else [{"type": "OUTPUT", "port": "NORMAL"}]
    
    flow = {
        "priority": priority,
        "timeout": 0,
        "isPermanent": True,
        "deviceId": device_id,
        "treatment": {"instructions": instructions},
        "selector": {
            "criteria": [
                {"type": "ETH_TYPE", "ethType": "0x0800"},  # IPv4
                {"type": "IPV4_SRC", "ip": src_ip},
                {"type": "IPV4_DST", "ip": dst_ip}
            ]
        }
    }
    
    resp = requests.post(
        f"{BASE_URL}/flows/{device_id}",
        data=json.dumps({"flows": [flow]}),
        headers=HEADERS,
        auth=AUTH
    )
    
    if resp.status_code in [200, 201]:
        print(f"✓ Rule added: {src_ip} -> {dst_ip} = {action}")
    else:
        print(f"✗ Error: {resp.status_code} - {resp.text}")

def apply_security_policy():
    """Применить политику изоляции гостевой сети"""
    device_id = get_device_id()
    if not device_id:
        return
    
    # Заблокировать доступ из гостевой сети (10.0.2.0/24) в рабочую (10.0.1.0/24)
    add_flow_rule(device_id, 40000, "10.0.2.0/24", "10.0.1.1/32", "DROP")
    add_flow_rule(device_id, 40000, "10.0.2.0/24", "10.0.1.2/32", "DROP")
    add_flow_rule(device_id, 40000, "10.0.2.0/24", "10.0.1.0/24", "DROP")
    
    print("\n✅ Policy applied! Guest network is isolated from Work network.")

if __name__ == "__main__":
    apply_security_policy()
```

### 4.4. docker-compose.yml — Запуск ONOS

```yaml
version: '3'
services:
  onos:
    image: onosproject/onos:latest
    container_name: onos
    ports:
      - "6653:6653"  # OpenFlow
      - "8181:8181"  # REST API / Web UI
      - "8101:8101"  # Karaf CLI
    restart: unless-stopped
```

**Запуск:**
```bash
docker-compose up -d
```

---

## 5. **Пошаговое выполнение**

### Шаг 1: Запуск ONOS

```bash
# Запустить через docker-compose
cd scenario_1
docker-compose up -d

# Или одной командой:
sudo docker run --name onos --rm \
  -p 6653:6653 -p 8181:8181 -p 8101:8101 \
  -d onosproject/onos

# Подождать ~30 секунд и проверить:
sudo docker ps
```

### Шаг 2: Активация приложений в ONOS

```bash
# Подключиться к консоли Karaf
ssh -p 8101 -o StrictHostKeyChecking=no karaf@localhost
# Пароль: karaf

# Внутри консоли активировать нужные приложения:
app activate org.onosproject.openflow
app activate org.onosproject.fwd
app activate org.onosproject.acl

# Проверить что приложения активны:
app list | grep -E "openflow|fwd|acl"

# Выйти из консоли:
logout
```

### Шаг 3: Настройка версии OpenFlow

```bash
# Убедиться что OVS использует OpenFlow 1.3 (совместим с ONOS)
sudo ovs-vsctl set bridge s1 protocols=OpenFlow13

# Проверить:
sudo ovs-vsctl get bridge s1 protocols
# Должно вернуть: ["OpenFlow13"]
```

### Шаг 4: Запуск топологии

```bash
# Запустить топологию
sudo python3 topology.py

# Дождаться появления приглашения mininet>
```

### Шаг 5: Проверка подключения к ONOS

```bash
# В новом терминале подключиться к ONOS:
ssh -p 8101 -o StrictHostKeyChecking=no karaf@localhost

# Проверить что коммутатор подключён:
devices
# Должно показать: of:0000000000000001, available=true

# Проверить обнаруженные хосты:
hosts
# Должны быть видны все 4 хоста с их IP-адресами
```

### Шаг 6: Применение политики безопасности

```bash
# В новом терминале (не закрывая Mininet):
python3 security_policy.py

# Ожидаемый вывод:
# ✓ Rule added: 10.0.2.0/24 -> 10.0.1.1/32 = DROP
# ✓ Rule added: 10.0.2.0/24 -> 10.0.1.2/32 = DROP
# ✓ Rule added: 10.0.2.0/24 -> 10.0.1.0/24 = DROP
# ✅ Policy applied!
```

### Шаг 7: Тестирование результата

```bash
# Вернуться в терминал с Mininet и выполнить тесты:

# ✅ Внутри рабочей сети — должно работать
mininet> h1 ping -c 3 h2

# ✅ Внутри гостевой сети — должно работать
mininet> h3 ping -c 3 h4

# ❌ Гость → Работа — должно быть заблокировано
mininet> h3 ping -c 3 h1
mininet> h3 ping -c 3 h2
```

---

## 6. **Демонстрация результата**

### 6.1. Ожидаемые результаты тестов

| Тест | Команда | Ожидаемый результат | Статус |
|------|---------|-------------------|--------|
| **Рабочая → Рабочая** | `h1 ping h2` | 0% loss, ~1ms | ✅ |
| **Гостевая → Гостевая** | `h3 ping h4` | 0% loss, ~1ms | ✅ |
| **Гостевая → Рабочая** | `h3 ping h1` | 100% loss | ✅ Заблокировано |
| **Гостевая → Рабочая** | `h3 ping h2` | 100% loss | ✅ Заблокировано |

### 6.2. Пример вывода

```
# ✅ Внутри рабочей сети
mininet> h1 ping -c 3 h2
64 bytes from 10.0.1.2: icmp_seq=1 ttl=64 time=0.068 ms
64 bytes from 10.0.1.2: icmp_seq=2 ttl=64 time=0.377 ms
64 bytes from 10.0.1.2: icmp_seq=3 ttl=64 time=7.57 ms
--- 10.0.1.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss

# ❌ Гость пытается пинговать рабочую сеть
mininet> h3 ping -c 3 h1
From 10.0.2.1 icmp_seq=1 Destination Host Unreachable
From 10.0.2.1 icmp_seq=2 Destination Host Unreachable
From 10.0.2.1 icmp_seq=3 Destination Host Unreachable
--- 10.0.1.1 ping statistics ---
3 packets transmitted, 0 received, +3 errors, 100% packet loss
```

---

## 7. **Презентация**

### 7.1. Быстрый чеклист

```bash
# ===== ПЕРЕД ПРЕЗЕНТАЦИЕЙ =====

# 1. Проверить что ONOS запущен
sudo docker ps

# 2. Проверить подключение свитча
sudo ovs-vsctl show | grep -A2 "Controller"

# 3. Проверить в ONOS (через Karaf)
ssh -p 8101 karaf@localhost
# Внутри:
devices
hosts
# Выйти: logout

# ===== ВО ВРЕМЯ ПРЕЗЕНТАЦИИ =====

# 4. Запустить топологию (если не запущена)
sudo python3 topology.py

# 5. В mininet> показать связность внутри подсетей
mininet> h1 ping -c 3 h2    # ✅ Работает
mininet> h3 ping -c 3 h4    # ✅ Работает

# 6. Показать блокировку между подсетями
mininet> h3 ping -c 3 h1    # ❌ Заблокировано
mininet> h3 ping -c 3 h2    # ❌ Заблокировано

# 7. (Опционально) Применить политику заново
# В новом терминале:
python3 security_policy.py
```

### 7.2. Сценарий демонстрации (3-5 минут)

| Время | Действие | Команда / Что показать |
|-------|----------|----------------------|
| 0:00-0:30 | Вступление | Показать схему архитектуры |
| 0:30-1:00 | ONOS запущен | `docker ps`, веб-интерфейс |
| 1:00-1:30 | Свитч подключён | `devices` в Karaf |
| 1:30-2:30 | Тест внутри подсетей | `h1 ping h2`, `h3 ping h4` |
| 2:30-3:30 | Тест изоляции | `h3 ping h1` — 100% loss |
| 3:30-4:00 | Показать код | `cat security_policy.py` |
| 4:00-5:00 | Выводы | Преимущества SDN |

---

## 8. **Пояснения к скриншотам**

### 8.1. `docker ps` — ONOS запущен

```
CONTAINER ID   IMAGE              STATUS   PORTS
xxxxxx         onosproject/onos   Up       6653, 8181, 8101
```

> **Пояснение:** Контроллер ONOS работает в Docker-контейнере. Открыты порты:  
> • `6653` — для OpenFlow-соединения со свитчами  
> • `8181` — для веб-интерфейса и REST API  
> • `8101` — для консоли управления (Karaf CLI)

---

### 8.2. `ovs-vsctl show` — Свитч подключён к контроллеру

```
Bridge s1
    Controller "tcp:127.0.0.1:6653"
        is_connected: true
    Port s1-eth1 ... s1-eth4
```

> **Пояснение:** Программный коммутатор s1 успешно подключён к ONOS.  
> Статус `is_connected: true` означает что контроллер управляет свитчем.  
> Видны 4 порта — по одному на каждый хост топологии.

---

### 8.3. `devices` в ONOS — Контроллер видит свитч

```
id=of:0000000000000001, available=true, local-status=connected, 
role=MASTER, protocol=OF_13
```

> **Пояснение:** ONOS подтверждает что видит коммутатор и управляет им.  
> • `available=true` — свитч доступен  
> • `role=MASTER` — ONOS принимает все решения о маршрутизации  
> • `protocol=OF_13` — используется OpenFlow 1.3

---

### 8.4. `hosts` в ONOS — Все хосты обнаружены

```
id=... ip(s)=[10.0.1.1], locations=[of:.../1]  ← h1, порт 1
id=... ip(s)=[10.0.1.2], locations=[of:.../2]  ← h2, порт 2
id=... ip(s)=[10.0.2.1], locations=[of:.../3]  ← h3, порт 3
id=... ip(s)=[10.0.2.2], locations=[of:.../4]  ← h4, порт 4
```

> **Пояснение:** ONOS автоматически обнаружил все хосты и знает на каком порту 
> каждый из них подключён. Рабочие хосты (10.0.1.х) на портах 1-2, 
> гостевые (10.0.2.х) на портах 3-4.

---

### 8.5. `pingall` — Общая картина изоляции

```
h1 -> h2 X X    ← h1 видит h2 (рабочая сеть)
h2 -> h1 X X    ← h2 видит h1 (рабочая сеть)
h3 -> X X h4    ← h3 видит h4 (гостевая сеть)
h4 -> X X h3    ← h4 видит h3 (гостевая сеть)
```

> **Пояснение:** Хосты внутри одной подсети видят друг друга, 
> а хосты из разных подсетей — нет. Это и есть изоляция гостевой сети.

---

### 8.6. `h3 ping h1` — Политика безопасности работает

```
From 10.0.2.1 icmp_seq=1 Destination Host Unreachable
...
3 packets transmitted, 0 received, 100% packet loss
```

> **Пояснение:** Гостевой хост пытается достучаться до рабочей сети, 
> но получает отказ. 100% потеря пакетов = политика изоляции работает.

---

### 8.7. `h1 ping h2` — Рабочая сеть работает нормально

```
64 bytes from 10.0.1.2: time=0.068 ms
3 packets transmitted, 3 received, 0% packet loss
```

> **Пояснение:** Внутри рабочей сети связь работает без ограничений. 
> Минимальная задержка, нет потерь — сотрудники могут работать.


---

## **Устранение неполадок**

| Проблема | Причина | Решение |
|----------|---------|---------|
| **ONOS не скачивается** | IPv6 в Docker | Отключить IPv6: `sysctl -w net.ipv6.conf.all.disable_ipv6=1` |
| **Свитч не подключается** | Неправильный IP контроллера | Указать в `topology.py` реальный IP VM |
| **Ошибка OFParseError** | Несоответствие версий OpenFlow | `ovs-vsctl set bridge s1 protocols=OpenFlow13` |
| **403 в веб-интерфейсе** | Не активирован GUI | В Karaf: `app activate org.onosproject.gui2` |
| **Хосты не пингуются** | Нет правил форвардинга | В Karaf: `app activate org.onosproject.fwd` |

---

## 📎 **Приложения**

### А. Глоссарий

| Термин | Определение |
|--------|-------------|
| **SDN** | Software-Defined Networking — архитектура с разделением плоскостей управления и данных |
| **OpenFlow** | Протокол для управления таблицами потоков в коммутаторах |
| **ONOS** | Open Network Operating System — SDN-контроллер с открытым исходным кодом |
| **Mininet** | Эмулятор сетей для тестирования протоколов и контроллеров |
| **OVS** | Open vSwitch — виртуальный многоуровневый коммутатор |
| **Karaf** | Консоль управления ONOS через SSH |

### Б. Полезные ссылки

- [ONOS Documentation](https://wiki.onosproject.org/)
- [Mininet Documentation](http://mininet.org/)
- [OpenFlow Specification](https://opennetworking.org/sdn-resources/openflow/)
- [GitHub Repository](https://github.com/GlebTovpeko/SDN_controller)
