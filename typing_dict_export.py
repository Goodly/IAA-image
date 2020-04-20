import json

typing_dict = {
        'Source relevance':
            {
                1: ['checklist', 9],
                2: ['nominal', 2],
                3: ['ordinal', 6],
                4: ['ordinal', 8]
            },
        #OLD
        'Science and Causality Questions for SSS Students V2':
            {
                5:['nominal', 1],
                6: ['checklist', 8],
                9:['ordinal', 4],
                10:['nominal', 1]
            },
        #OLD
        'Language Specialist V2':
            {
                1:['checklist',9],
                6:['checklist', 8],

            },
        'Language Specialist V3':
            {
                1:['checklist', 13],
                2:['ordinal', 5],
                3:['ordinal', 5],
                4:['ordinal', 6],
                5:['checklist', 8],
                6:['nominal', 1],
                7:['ordinal',5],
                8:['ordinal', 5],
                9:['ordinal', 5],
                10: ['ordinal', 5],
                11: ['ordinal', 4],
                12: ['ordinal', 10],
                13: ['ordinal', 10],
                15: ['ordinal', 10]
            },
        'Language Specialist V4':
            {
                1:['checklist', 13],
                2:['ordinal', 5],
                3:['ordinal',5],
                5:['ordinal', 5],
                6:['ordinal', 8],
                7:['nominal', 1],
                9:['ordinal', 5],
                10:['ordinal',4],
                11:['ordinal',5],
                12:['ordinal', 4],
                13:['ordinal', 5],
                14:['ordinal', 10],
                15:['ordinal', 10]

            },
        'Confidence':
            {
                1:['ordinal', 3],
                2:['ordinal', 5],
                4:['ordinal', 3],
                5:['ordinal', 3],
                6:['nominal', 5],
                7:['ordinal', 3],
                8:['ordinal', 5],
                9:['ordinal', 5],
                10:['ordinal', 3],
                11:['ordinal', 4],
                12:['checklist', 4],
                13:['ordinal', 10],
                14:['ordinal', 10]
            },
        'Probability Specialist':
            {
                1: ['ordinal', 3],
                2: ['ordinal', 5],
                4: ['ordinal', 3],
                5: ['ordinal', 3],
                6: ['nominal', 5],
                7: ['nominal', 5],
                8: ['ordinal', 5],
                9: ['ordinal', 5],
                10: ['ordinal', 3],
                11: ['ordinal', 4],
                12: ['nominal', 5],
                13: ['ordinal', 10],
                14: ['ordinal', 10]
            },
        'Reasoning Specialist':
            {
                1: ['checklist', 6],
                2:['checklist', 6],
                3: ['checklist', 7],
                4: ['ordinal', 3],
                5: ['ordinal', 3],
                6: ['checklist', 10],
                7: ['ordinal', 5],
                8: ['nominal', 1],
                9: ['ordinal', 10],
                10: ['ordinal', 10]
            },
        'Probability Specialist V4':
            {
                1: ['ordinal', 3],
                2: ['ordinal', 5],
                5: ['ordinal', 3],
                6: ['ordinal', 3],
                7: ['ordinal', 5],
                10: ['ordinal', 3],
                11: ['ordinal', 4],
                12: ['ordinal', 5],
                13: ['ordinal', 10],
                14: ['ordinal', 10]
            },
        'Evidence Specialist':
            {
                1:['checklist', 3],
                2:['checklist', 9],
                #TODO: this is an interval quesiton, prob gonna get ignored l8r though
                3:['nominal', 1],
                4:['ordinal', 6],
                5:['ordinal', 5],
                6:['nominal', 3],
                7:['nominal', 1],
                8:['ordinal', 5],
                9:['ordinal', 3],
                10:['ordinal', 5],
                11:['ordinal', 5],
                12:['ordinal', 4],
                13:['ordinal', 10],
                14:['ordinal', 10]
            },
        'Evidence Specialist 3':
            {
                1: ['checklist', 3],
                2: ['checklist', 9],
                # TODO: this is an interval quesiton, prob gonna get ignored l8r though
                3: ['nominal', 1],
                4: ['ordinal', 5],
                5: ['ordinal', 6],
                6: ['ordinal', 6],
                7: ['nominal', 3],
                8: ['nominal', 1],
                9: ['ordinal', 7],
                10: ['ordinal', 3],
                11: ['ordinal', 5],
                12: ['ordinal', 5],
                13: ['ordinal', 4],
                14: ['ordinal', 10],
                15: ['nominal', 1]
            },
        'Beginner Reasoning Specialist Structured':
            {
                1:['checklist', 5],
                2:['checklist', 6],
                3:['checklist', 7],
                4:['ordinal', 3],
                5:['ordinal', 3],
                6:['checklist', 9],
                7:['ordinal', 6],
                8:['nominal', 1],
                #hardness
                9:['ordinal', 10],
                #confidence
                10:['ordinal', 10]
            },
        'Evidence':
            {
                5:['ordinal', 3],
                6:['checklist', 7],
                12:['nominal', 1]

            },
        'Argument relevance':
            {
                1:['ordinal', 6],
                2: ['ordinal', 10],
                3: ['ordinal', 10]
            },
        'Source relevance':
            {
                1:['checklist', 9],
                2:['checklist', 2],
                3:['checklist', 6],
                4:['ordinal', 8],
                5:['ordinal', 10],
                6:['ordinal', 10]
            },
        'Quote Source Relevance':
            {
                1: ['nominal', 2],
                2: ['ordinal', 8],
                3: ['nominal', 2],
                4: ['checklist', 9],
                5: ['checklist', 9],
                6: ['checklist', 2],
                7: ['checklist', 6],
                8: ['ordinal', 7],
                9: ['ordinal', 10],
                10: ['ordinal', 10]
            },
        'Probability':
            {
                1:['ordinal', 3],
                2:['ordinal', 5],
                3:['ordinal', 3],
                4:['ordinal', 7],
                5:['ordinal', 3],
                6:['ordinal', 3],
                7:['ordinal', 5],
                8:['ordinal',10],
                9:['nominal', 1],
                10:['ordinal', 3],
                11:['ordinal', 4],
                12:['ordinal', 5],
                13:['ordinal', 10],
                14:['ordinal', 10]


            },
        'Holistic Evaluation of Article':
            {
                1: ['nominal', 9],
                2: ['nominal',1],
                3: ['checklist', 12],
                4: ['nominal',1],
                5: ['ordinal',5],
                6: ['checklist',8],
                7: ['ordinal', 5],
                8: ['ordinal', 5],
                9: ['checklist', 9],
                10: ['ordinal', 5],
                11: ['ordinal', 4],
                12: ['ordinal', 5],
                13: ['checklist', 5],
                14: ['nominal', 2],
                15: ['checklist', 3],
                16: ['nominal', 1],
                17: ['ordinal', 10],
                18: ['ordinal', 10]
            }
    }

with open('./config/typing_dict.txt', 'w') as file:
    json.dump(typing_dict, file)