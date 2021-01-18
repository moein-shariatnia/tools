from IPython.display import display
import ipywidgets as widgets

import os
import pandas as pd


class ImageLabler:
    def __init__(
        self,
        df,
        description="View Type",
        options=["AP", "Axial", "Y", "Not_specified"],
        default="Not_specified",
        show_id=True,
        file_name="labeled",
        exists=True,
    ):
        self.df = df
        self.paths = df.sample(len(df))["path"].values
        self.counter = 0
        self.name = file_name
        self.description = description
        self.options = options
        self.default = default
        self.show_id = show_id
        if exists:
            labeled_df = pd.read_csv(f"{file_name}.csv")
            already_labeled = labeled_df["path"].values
            self.paths = [p for p in self.paths if p not in already_labeled]
            self.labeled_df = labeled_df
        else:
            self.labeled_df = None

        self.current_img = None
        self.current_id = None
        self.current_label = self.default
        self.current_path = None
        self.labeled_imgs = {}

        self.img_w = None
        self.id_w = None
        self.dropdown_w = None
        self.next_w = None
        self.save_w = None

        self.run(first=True)
        self.build_widgets()

        vbox = widgets.VBox([self.id_w, self.img_w, self.dropdown_w])
        hbox = widgets.HBox([self.next_w, self.save_w])
        display(widgets.VBox([vbox, hbox]))

    def build_widgets(self):
        self.id_w = widgets.Label(value=self.current_id)
        self.img_w = widgets.Image(
            value=self.current_img, format="png", width=200, height=200
        )

        self.dropdown_w = widgets.Dropdown(
            options=self.options,
            value=self.default,
            description=self.description,
            disabled=False,
        )

        def dropdown_event(change):
            if change["type"] == "change" and change["name"] == "value":
                self.current_label = change.new
                print(f"You have selected: {change.new}")

        self.dropdown_w.observe(dropdown_event)

        self.next_w = widgets.Button(description="Next")

        def next_event(click):
            self.counter += 1
            self.labeled_imgs[self.current_path] = self.current_label
            self.run()

        self.next_w.on_click(next_event)

        self.save_w = widgets.Button(description="Save")

        def save_event(click):
            labeled_df = pd.DataFrame(
                {"path": self.labeled_imgs.keys(), "label": self.labeled_imgs.values()}
            )
            try:
                loaded = pd.read_csv(f"{self.name}.csv")
                os.remove(f"{self.name}.csv")
                labeled_df = pd.concat([labeled_df, loaded], axis=0).reset_index(
                    drop=True
                )
                labeled_df.to_csv(f"{self.name}.csv", index=False)
                self.labeled_df = labeled_df
            except:
                labeled_df.to_csv(f"{self.name}.csv", index=False)
                self.labeled_df = labeled_df

            self.labeled_imgs = {}

        self.save_w.on_click(save_event)

    def run(self, first=False):
        self.current_path = self.paths[self.counter]
        self.current_img = open(self.current_path, "rb").read()
        if self.show_id:
            img_id = self.current_path.split("/")
            img_id = "_".join(img_id[-3:])
            self.current_id = f"Image number: {self.counter} | Image id: {img_id}"
        else:
            self.current_id = f"Image number: {self.counter}"
        if not first:
            self.img_w.value = self.current_img
            self.id_w.value = self.current_id
            self.dropdown_w.value = self.default
            self.current_label = self.default

