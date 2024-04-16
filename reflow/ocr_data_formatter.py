from typing import Union, List


class OCRDataFormatter:
    def __init__(self):
        pass

    def index_order(self, index: dict):
        return (
            index["page_num"] * 1000000
            + index["block_num"] * 10000
            + index["par_num"] * 100
            + index["line_num"]
        )

    def combine_rect(self, rect1, rect2):
        return {
            "left": min(rect1["left"], rect2["left"]),
            "top": min(rect1["top"], rect2["top"]),
            "width": max(rect1["left"] + rect1["width"], rect2["left"] + rect2["width"])
            - min(rect1["left"], rect2["left"]),
            "height": max(
                rect1["top"] + rect1["height"], rect2["top"] + rect2["height"]
            )
            - min(rect1["top"], rect2["top"]),
        }

    def format_output_to_hirerachy(self, output: Union[dict, List[dict]]):
        if isinstance(output, list):
            pages = []
            for page in output:
                pages.append(self.format_output_to_hirerachy(page))
            return pages
        words = self.group_text_by_words(output)
        boxes = self.group_words(words)
        return boxes

    def group_text_by_words(self, output: dict):
        level = output["level"]
        page_num = output["page_num"]
        block_num = output["block_num"]
        par_num = output["par_num"]
        line_num = output["line_num"]
        word_num = output["word_num"]
        left = output["left"]
        top = output["top"]
        width = output["width"]
        height = output["height"]
        conf = output["conf"]
        text = output["text"]

        words = []

        for i in range(len(level)):
            word = {
                "level": level[i],
                "index": {
                    "page_num": page_num[i],
                    "block_num": block_num[i],
                    "par_num": par_num[i],
                    "line_num": line_num[i],
                    "word_num": word_num[i],
                },
                "rect": {
                    "left": left[i],
                    "top": top[i],
                    "width": width[i],
                    "height": height[i],
                },
                "conf": conf[i],
                "text": text[i],
            }
            words += [word]

        return words

    def group_words(self, words: list):
        boxes = []

        base_level = ["block", "par", "line", "word"]

        def append_word(base_list, word, hier_level):
            if word['index']['block_num'] == 0:
                return
            
            if hier_level >= len(base_level) - 1:
                if word["index"]["word_num"] == 0:
                    
                    return
                base_list.append(word)
                return

            level_num = f"{base_level[hier_level]}_num"
            level_index = word["index"][level_num]
            while len(base_list) <= level_index:
                base_list.append(
                    {
                        "level": hier_level,
                        "index": word['index'],
                        "children": [],
                        "rect": word["rect"],
                    }
                )
                
            if word["index"][f"{base_level[hier_level + 1]}_num"] == 0:
                base_list[level_index]["rect"] = word["rect"]
                if hier_level == 2:
                    base_list[level_index]["font_size"] = word["rect"]["height"]
                return
           
            append_word(base_list[level_index]["children"], word, hier_level + 1)

            #if hier_level < 2 and "font_size" in base_list[level_index]["children"][0]:
            #    base_list[level_index]["font_size"] = base_list[level_index]["children"][0]["font_size"]
            
        for word in words:
            append_word(boxes, word, 0)

        return boxes
