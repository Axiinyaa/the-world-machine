

import utilities.bot_icons as icons


def text(data: dict = {}):
    
    # Generally, you want to leave this code alone. Unless you want to do something fancy.
    def fetch(what: str):
        return data.get(what, "?")

    # Simply renaming variables so that it makes things easier to read.
    loading_icon = icons.icon_loading
    wool_icon = icons.icon_wool

    # Start of translations
    return {
        "General": {
            "loading": f"[ {loading_icon} **Загрузка...** ]",
            "loading_cmd": f"[ {loading_icon} **Обработка...** ]",
        },
        
        "Shop": {
            "user_wool": f'Сейчас у вас есть: {wool_icon}**{fetch("wool")}**',
            "stock": f'*Стоковое значение:* `{fetch("stock_value")}`\n*Стоковая цена:* `{fetch("stock_price")}`',
            
            "key_owned": '🔴 - Уже есть \n ⚪ - Не можете позволить себе',
            "key_general": '⚪ - Не можете позволить себе',
            
            "go_back": "Назад",  # Button for when a user wants to go back to the main shop.
            "buy": "Купить",  # Button for when a user buys something.
            "buy_all": "Скупить всё",

            "sell_button": "Продать сокровища",
            "sell": "Продать одно",
            "sell_all": f"Продать всё (x{fetch('amount')})",
            
            "cannot_buy": "У вас недостаточно шерсти для обмена на этот товар.",
            "cannot_sell": "У вас нет ничего на обмен.",
            "already_owned": "У вас уже есть этот предмет.",
            
            "bought": f'Успешно обменяно {fetch("cost")} Шерсти на {fetch("what")}!',
            "bought_all": f'Успешно обменяно {fetch("cost")} Шерсти на {fetch("amount")} {fetch("what")}(s)!',
            
            "sold": f'Успешно продано {fetch("what")} для {fetch("cost")} Шерсти!',
            "sold_all": f'Успешно продано {fetch("amount")} {fetch("what")}(s) для {fetch("cost")} Шерсти!',
            
            "currently_owned": f'В данный момент есть: **{fetch("amount")}**',
            
            "MainShop": {
                "title": "Добро пожаловать в Магазин!",
                
                "description": f"""
                    Хей-эй! Добро пожаловать в мою лавку. Я здесь всегда в поисках ради самых интересных сокровищ и {wool_icon}**Шерсти**...! Я готов обменять множество блестящих и красочных украшений, фон, капсулы и многое другое на твою шерсть... Думай об шерсти как о валюте, ага?

                    Чтобы начать, просто выбери одну из категорий которую я предоставляю и затем меняйся прямо сейчас! Имей в виду, что есть здесь некоторые предметы, которые меняются **каждый день**, поэтому следи за ними!
                    
                    {fetch("motd")}
                    
                    {fetch("user_wool")}
                    """,
                    
                "motds": [
                    "Шерстяной рынок меняется каждый день. Честно, мы, Птице-люди, имеем насчёт этого хорошую интуицию, и под своей интуицией я подразумеваю, что я рандомно увеличивую или уменьшаю его тогда, пока мне хочется.",
                    "Может быть я и *сломал* рынок разок или два. Давай это будет только между нами, ок?",
                    "Умные слова, как от друга: Если ты будешь продавать дёшего, а покупать дорого, то у вас будет хорошая удача..! Не думай даже это проверять!",
                    "Мою бедную повозку с сокровищами смыло течением... Может, ты найдёшь для меня ещё что-нибудь?",
                    "Ты спрашиваешь, что же случилось с торговцем, работающим до меня? Я бы не знал. Я бы вообще не знал...", # During the World Machine Edition AMA Nightmargin jokingly said that Magpie hid a body which has not been found yet. Considering the fact that the purple trader is nowhere to be found in the remake, it is the most likely victim of this alleged crime.
                    "Тебе нравится моя бутыльная коллекция? Мне она нравится. Ты знаешь что значит \"Крепкий Ликёр\"? ?", # Magpie's drink of choice is hard liquor, but only so he can collect the bottles afterwards.
                ],
                
                "buttons": {
                    # Translate right hand values (e.g. 'capsules': 'Гасипон')
                    "capsules": "Капсулы",
                    "pancakes": "Панкейки",
                    "Backgrounds": "Фоны",
                    "Treasures": "Сокровища",
                },
            },
            
            "Capsules": {
                "title": "Капсулы",
                "description": f"""
                    Хочешь компаньона к своему путешествию? Теперь ты можешь купить одну их этих капсул! При покупке одного, вы можете выбить себе случайного **Никоготчи**! Чем более редкая капсула, тем более крутой Никоготчи!
        
                    После покупки Никоготчи, введи </nikogotchi check:1149412792919674973> чтобы увидеть своего нового друга! Убедись, что ты заботишься о нём, или если их потребности будут не удовлетворены, у них может кончиться здоровье и они умрут...
                    
                    Кормите их панкейками, мойте их и уделяйте им внимание, и ваш Никоготчи будет жить многие года! Мыть их и уделять внимание - это ещё легко, но тебе надо будет покупать им панкейки у меня!
                    
                    Ещё просто помни, что ты можешь иметь у себя только одного Никоготчи за раз. Единственный выбор получить ещё одного это отослать их прочь или если они уже умерли.
                    
                    {fetch("capsules")}
                    {fetch("key")}
                    
                    {fetch("user_wool")}
                    """,
            },
            
            "Pancakes": {
                "title": "Панкейки",
                "description": f"""
                    Корми своего Никоготчи ими! У них есть разные эффекты - от делания вашего Никоготчи счастливым до полного исцеления их здоровья от всего!
                    
                    {fetch("pancakes")}
                    {fetch("key")}
                    
                    {fetch("user_wool")}
                    """,
            },
            
            "Backgrounds": {
                "title": "Фоны",
                "description": f'Хочешь купить **{fetch("name")}** за {wool_icon}{fetch("cost")}?\n\n{fetch("key")}\n\n{fetch("user_wool")}',
            },
            
            "Treasures": {
                "title": "Сокровища",
                "description": f"""
                Ничего себе! Похоже ты заинтересован в покупке моих сокровищ. Я получал эти штучки от торговцев всего мира, с Пустошей даже до Убежища!
                
                Ты можешь снять эти блестящие и фантастические сокровища с моих перьев только своей шерстью!!

                O-о! И конечно, ты можешь обменивать **свои** сокровища, чтобы получить шерсть обратно... Думай об этом, как о продаже.

                Учти, что сток шерстянного рынка меняется каждый день, так что убедись в своей возможности купить что-либо!
                
                ***Шерстянной рынок:***
                
                {fetch('wool_market')}

                ***Сток сокровищ:***
                {fetch('treasures')}
                
                {fetch('key')}
                {fetch('user_wool')}
                """
            },
            
            "Treasure_Sell": {
                "title": "Sell Treasures",
                "description": f"""
                А-а-а... Хочешь обменять немного сокровищ ради {wool_icon}Шерсти? Ну, тебе сегодня везёт!
                
                Просто выбери сокровище и укажи, сколько ты будешь обменимать!
                
                Ещё помни, что *шерстянной рынок* решает, сколько ты получишь обратно.
                
                ***Шерстянной рынок:***
                
                {fetch('wool_market')}
                
                ***Выбранное сокровище:***
                
                {fetch('selected_treasure')}
                
                
                {fetch('user_wool')}
                """,
                
                "select_no_treasures :(": f"У тебя нет не единого сокровища!",
                "select_treasure_placeholder": f"Выбери сокровище!",
            
                "treasure_not_selected": "Видимо, ты ещё не выбрал, что продашь... Дай мне знать, когда выберешь!",
                "treasure_selected": f"О-о-о... **{fetch('selected_treasure')}** Я думаю, я могу дать тебе {wool_icon}**{fetch('sell_one')}**, Если ты дашь мне одно, но могу {wool_icon}**{fetch('sell_all')}** если ты мне отдашь всё!",
            },
        },
        
        "Items": {
            # Translate 'name' and 'description' values.
            "Treasures": {
                "bottle": {
                    "name": "Бутылка Алкоголя",
                    "description": "Этот запах просто отвратителен. Хорош для коктейля Молотова.",
                },
                "shirt": {
                    "name": "Сувенирная Кофта",
                    "description": '"Я пас баранов, и всё что мне дали - эта дранная кофта!"',
                },
                "journal": {
                    "name": "Мистический Журнал",
                    "description": "Он написанн на неизвестном языке.",
                },
                "amber": {
                    "name": "Янтарный Медальон",
                    "description": "Кусочек светящегося янтаря с чёрным клевером внутри.",
                },
                "pen": {
                    "name": "Светящаяся ручка",
                    "description": "Длинное перо со светящимися краями.",
                },
                "card": {
                    "name": '"Реальная" Пропускная Карта',
                    "description": "Здесь приклеено фото Нико.",
                },
                "die": {
                    "name": "Светящаяся игральная кость",
                    "description": "Игральная кость со светящимися точками.",
                },
                "sun": {
                    "name": "Лампочка",
                    "description": "Огромная лампа. Это солнце.",
                },
                "clover": {
                    "name": "Светящийся клевер",
                    "description": "Клевер. Светится золотым цветом.",
                },
            },
            "capsules": {
                "blue": {
                    "name": "Синяя капсула",
                    "description": "Связан с синим фосфором, эта капсула даст тебе обыкновенного Никоготчи.",
                },
                "green": {
                    "name": "Зелёная капсула",
                    "description": "Связан с зелёным фосфором, эта капсула даст тебе необыкновенного Никоготчи.",
                },
                "red": {
                    "name": "Красная капсула",
                    "description": "Связан красным фосфором, эта капсула даст тебе редкого Никоготчи.",
                },
                "yellow": {
                    "name": "Yellow Capsule",
                    "description": "Связан жёлтым фосфором, эта капсула даст тебе очень редкого Никоготчи.",
                },
            },
            "pancakes": {
                "pancakes": {
                    "name": "Панкейки",
                    "description": "+1 Здоровья and +25 Сытости",
                },
                "golden_pancakes": {
                    "name": "Золотые Панкейки",
                    "description": "+25 Здоровья and +50 Сытости",
                },
                "glitched_pancakes": {
                    "name": "???",
                    "description": "Я даже понятия не имею, что они тут делают.",
                },
            },
            "Backgrounds": {
                # Translate the right hand value. (e.g. 'Normal': 'Translate This.')
                "Default": "Нормальный",
                "Green": "Зелёный",
                "Yellow": "Жёлтый",
                "Pink": "Розовый",
                "Red": "Красный",
                "Blue": "Синий",
                "Barrens": "Пустоши",
                "Glens": "Долина",
                "Refuge": "Убежище",
                "The Author": "Автор",
                "The World Machine": "Мировая Машина",
                "Alula and Calamus": "Алула и Каламус",
                "Pancakes": "Панкейки",
                "Magoie": "Мэгпай",
                "Catwalk": "Узкий Проход",
                "Ruins": "Руины",
                "Factory": "Фабрика",
                "Lamplighter": "Лэмплайтер",
                "Library": "Библиотека",
            },
        },
    }

