"use strict";
class NamedImpl {
    constructor(name) {
        this.name = name;
    }
}
const names = function (names) {
    return names.map(name => new NamedImpl(name));
};
class EmptyEnum {
    constructor(args) { }
}
const newEnum = function (enumProto, argsList) {
    return _a = class Enum extends enumProto {
            constructor(id, args) {
                super(args);
                this.order = (a, b) => a.id - b.id;
                this.id = id;
                this.name = args.name;
            }
            static createValueMap() {
                const map = new Map();
                Enum.values.forEach(value => {
                    map.set(value.name, value);
                });
                return map;
            }
            static getNullable(name) {
                return Enum.instances.get(name);
            }
            static get(name) {
                return Enum.getNullable(name);
            }
            compareTo(other) {
                return this.id - other.id;
            }
        },
        _a.values = argsList.map((args, i) => new _a(i, args)),
        _a.instances = _a.createValueMap(),
        _a;
    var _a;
};
class Category extends newEnum(EmptyEnum, names([
    "multiple",
    "boolean"
])) {
}
Category.MultipleChoice = Category.get("multiple");
Category.TrueOrFalse = Category.get("boolean");
class QuestionType extends newEnum(EmptyEnum, names([
    "easy",
    "medium",
    "hard"
])) {
}
QuestionType.Easy = Category.get("easy");
QuestionType.Medium = Category.get("medium");
QuestionType.Hard = Category.get("hard");
class Difficulty extends newEnum(EmptyEnum, names([
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
}
Difficulty.Any_Category = QuestionType.get("Any Category");
Difficulty.General_Knowledge = QuestionType.get("General Knowledge");
Difficulty.Entertainment_Books = QuestionType.get("Entertainment: Books");
Difficulty.Entertainment_Film = QuestionType.get("Entertainment: Film");
Difficulty.Entertainment_Music = QuestionType.get("Entertainment: Music");
Difficulty.Entertainment_Musicals_Theatres = QuestionType.get("Entertainment: Musicals & Theatres");
Difficulty.Entertainment_Television = QuestionType.get("Entertainment: Television");
Difficulty.Entertainment_Video_Games = QuestionType.get("Entertainment: Video Games");
Difficulty.Entertainment_Board_Games = QuestionType.get("Entertainment: Board Games");
Difficulty.Science_Nature = QuestionType.get("Science & Nature");
Difficulty.Science_Computers = QuestionType.get("Science: Computers");
Difficulty.Science_Mathematics = QuestionType.get("Science: Mathematics");
Difficulty.Mythology = QuestionType.get("Mythology");
Difficulty.Sports = QuestionType.get("Sports");
Difficulty.Geography = QuestionType.get("Geography");
Difficulty.History = QuestionType.get("History");
Difficulty.Politics = QuestionType.get("Politics");
Difficulty.Art = QuestionType.get("Art");
Difficulty.Celebrities = QuestionType.get("Celebrities");
Difficulty.Animals = QuestionType.get("Animals");
Difficulty.Vehicles = QuestionType.get("Vehicles");
Difficulty.Entertainment_Comics = QuestionType.get("Entertainment: Comics");
Difficulty.Science_Gadgets = QuestionType.get("Science: Gadgets");
Difficulty.Entertainment_Japanese_Anime_Manga = QuestionType.get("Entertainment: Japanese Anime & Manga");
Difficulty.Entertainment_Cartoon_Animations = QuestionType.get("Entertainment: Cartoon & Animations");
class Question {
    constructor(json) {
        this.category = Category.get(json.category);
        this.type = QuestionType.get(json.type);
        this.difficulty = Difficulty.get(json.difficulty);
        this.correctAnswer = json.correct_answer;
        this.answers = [this.correctAnswer];
        this.answers.push(json.incorrect_answers);
    }
}
