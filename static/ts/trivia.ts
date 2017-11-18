interface Comparable<T> {
    
    compareTo(t: T): number;
    
}

interface Ordered<T> {
    
    readonly order: (a: T, b: T) => number;
    
}

interface IdAble {
    
    readonly id: number;
    
}

interface Named {
    
    readonly name: string;
    
}

class NamedImpl implements Named {
    
    public readonly name: string;
    
    public constructor(name: string) {
        this.name = name;
    }
    
}

const names = function(names: string[]): Named[] {
    return names.map(name => new NamedImpl(name));
};

interface Properties<T> {
    
    [key: string]: T;
    
}

interface EnumCtor<CtorArgs> {
    
    new(args?: CtorArgs): any;
    
}

interface IEnum<T> {
    
    readonly values: T[];
    
    get(name: string): T | undefined;
    
    getNonNull(name: string): T;
    
}

class EmptyEnum {
    
    public constructor(args?: any) {}
    
}

const newEnum = function <T, CtorArgs>(enumProto: EnumCtor<CtorArgs>, argsList: (Named & CtorArgs)[]) {
    return class Enum extends enumProto implements Comparable<T>, Ordered<T> {
        
        private static createValueMap(): Map<string, T & Enum> {
            const map: Map<string, T & Enum> = new Map();
            Enum.values.forEach(value => {
                map.set(value.name, value);
            });
            return map;
        }
        
        public static readonly values: (T & Enum)[] =
            argsList.map((args: Named & CtorArgs, i: number) => <T & Enum> new Enum(i, args));
        
        private static readonly instances: Map<string, T & Enum> = Enum.createValueMap();
        
        public static getNullable(name: string): (T & Enum) | undefined {
            return Enum.instances.get(name);
        }
        
        public static get(name: string): T & Enum {
            return <T & Enum> Enum.getNullable(name);
        }
        
        public readonly id: number;
        public readonly name: string;
        
        public constructor(id: number, args: Named & CtorArgs) {
            super(<CtorArgs> args);
            this.id = id;
            this.name = args.name;
        }
        
        public compareTo(other: T & Enum): number {
            return this.id - other.id;
        }
        
        public order: (a: T & Enum, b: T & Enum) => number =
            (a: T & Enum, b: T & Enum) => a.id - b.id;
        
    }
};

class Category extends newEnum<Category, any>(EmptyEnum, names([
    "multiple",
    "boolean"
])) {
    
    public static readonly MultipleChoice: Category = Category.get("multiple");
    
    public static readonly TrueOrFalse: Category = Category.get("boolean");
    
}

class QuestionType extends newEnum<QuestionType, any>(EmptyEnum, names([
    "easy",
    "medium",
    "hard"
])) {
    
    public static readonly Easy: Category = Category.get("easy");
    
    public static readonly Medium: Category = Category.get("medium");
    
    public static readonly Hard: Category = Category.get("hard");
    
}

class Difficulty extends newEnum<Difficulty, any>(EmptyEnum, names([
    "Any Category",
    "General Knowledge",
    "Entertainment: Books",
    "Entertainment: Film",
    "Entertainment: Music",
    "Entertainment: Musicals & Theatres",
    "Entertainment: Television",
    "Entertainment: Video Games",
    "Entertainment: Board Games",
    "Science & Nature",
    "Science: Computers",
    "Science: Mathematics",
    "Mythology",
    "Sports",
    "Geography",
    "History",
    "Politics",
    "Art",
    "Celebrities",
    "Animals",
    "Vehicles",
    "Entertainment: Comics",
    "Science: Gadgets",
    "Entertainment: Japanese Anime & Manga",
    "Entertainment: Cartoon & Animations"
])) {
    
    public static readonly Any_Category: QuestionType =
            QuestionType.get("Any Category");

    public static readonly General_Knowledge: QuestionType =
            QuestionType.get("General Knowledge");

    public static readonly Entertainment_Books: QuestionType =
            QuestionType.get("Entertainment: Books");

    public static readonly Entertainment_Film: QuestionType =
            QuestionType.get("Entertainment: Film");

    public static readonly Entertainment_Music: QuestionType =
            QuestionType.get("Entertainment: Music");

    public static readonly Entertainment_Musicals_Theatres: QuestionType =
            QuestionType.get("Entertainment: Musicals & Theatres");

    public static readonly Entertainment_Television: QuestionType =
            QuestionType.get("Entertainment: Television");

    public static readonly Entertainment_Video_Games: QuestionType =
            QuestionType.get("Entertainment: Video Games");

    public static readonly Entertainment_Board_Games: QuestionType =
            QuestionType.get("Entertainment: Board Games");

    public static readonly Science_Nature: QuestionType =
            QuestionType.get("Science & Nature");

    public static readonly Science_Computers: QuestionType =
            QuestionType.get("Science: Computers");

    public static readonly Science_Mathematics: QuestionType =
            QuestionType.get("Science: Mathematics");

    public static readonly Mythology: QuestionType =
            QuestionType.get("Mythology");

    public static readonly Sports: QuestionType =
            QuestionType.get("Sports");

    public static readonly Geography: QuestionType =
            QuestionType.get("Geography");

    public static readonly History: QuestionType =
            QuestionType.get("History");

    public static readonly Politics: QuestionType =
            QuestionType.get("Politics");

    public static readonly Art: QuestionType =
            QuestionType.get("Art");

    public static readonly Celebrities: QuestionType =
            QuestionType.get("Celebrities");

    public static readonly Animals: QuestionType =
            QuestionType.get("Animals");

    public static readonly Vehicles: QuestionType =
            QuestionType.get("Vehicles");

    public static readonly Entertainment_Comics: QuestionType =
            QuestionType.get("Entertainment: Comics");

    public static readonly Science_Gadgets: QuestionType =
            QuestionType.get("Science: Gadgets");

    public static readonly Entertainment_Japanese_Anime_Manga: QuestionType =
            QuestionType.get("Entertainment: Japanese Anime & Manga");

    public static readonly Entertainment_Cartoon_Animations: QuestionType =
            QuestionType.get("Entertainment: Cartoon & Animations");
    
}

class Question {
    
    readonly category: Category;
    readonly type: QuestionType;
    readonly difficulty: Difficulty;
    readonly answers: Array<string>;
    readonly correctAnswer: string;
    
    public constructor(json: any) {
        this.category = Category.get(json.category);
        this.type = QuestionType.get(json.type);
        this.difficulty = Difficulty.get(json.difficulty);
        this.correctAnswer = json.correct_answer;
        this.answers = [this.correctAnswer];
        this.answers.push(json.incorrect_answers);
    }
    
}