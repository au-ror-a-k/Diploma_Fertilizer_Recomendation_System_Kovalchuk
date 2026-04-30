"""
Module for handling field-related information for the "Your Fields" page
and the Field page.
"""

import pandas as pd

from data_base.connection import get_connection


class YourFieldsSearch:
    """
    Class for handling information about a single field or all user fields.
    """

    ELEM_COLUMN_MAP = {
        "pH": "pH",
        "P": "P",
        "K": "K",
        "Mg": "Mg",
        "B": "B",
        "Cu": "Cu",
        "Mn": "Mn",
        "Zn": "Zn",
        "C.E.C": "CEC",
        "OM": "OM",
        "Fe": "Fe",
        "Ca": "Ca",
        "Na": "Na",
        "S": "S",
        "Mo": "Mo",
    }

    VALIDATE_NAME_MAP = {
        "Organic_M": "OM",
        "Organic M.": "OM",
        "Organic M": "OM",
    }

    def __init__(self, user_id):
        self.user_id = user_id

        self.connection = get_connection()
        self.cur = self.connection.cursor()

    def search_field_data(self, user_id, field_name):
        """
        Searches for field information for a specific user by a specific field name.
        """
        self.cur.execute(
            """
                SELECT soil_analysis, farm_name, crop_name
                FROM field_data
                WHERE user_id = %s AND field_name = %s
            """,
            (user_id, field_name),
        )
        result = self.cur.fetchall()

        if not result:
            return None

        all_fields = []

        for soil_analysis, farm_name, crop_name in result:
            temp = pd.DataFrame(soil_analysis)
            temp = temp.rename(columns={"Name": "zone_name"})
            temp = temp.rename(columns=self.VALIDATE_NAME_MAP)

            temp["farm_name"] = farm_name
            temp["field_name"] = field_name
            temp["crop_name"] = crop_name

            all_fields.append(temp)

        return pd.concat(all_fields, ignore_index=True)

    def get_guideline_data(self):
        """
        Retrieves information about soil chemical element level classifications,
        such as "Very low" or "High".
        """
        self.cur.execute(
            """
                SELECT *
                FROM elements_guideline
            """
        )
        result = self.cur.fetchall()

        if result:
            cols = [desc[0] for desc in self.cur.description]
            guideline_data = pd.DataFrame(result, columns=cols)
        else:
            guideline_data = None

        return guideline_data

    def color_grade_chem_level(self, field):
        """
        Assigns the appropriate color from the elements_guideline table
        to each element in each row of the field's chemical analysis data.
        """
        guideline = self.get_guideline_data()

        for (
            element_name_in_fields,
            element_name_in_guideline,
        ) in self.ELEM_COLUMN_MAP.items():
            element_data = guideline[
                guideline["short_elem_name"] == element_name_in_guideline
            ][["min_elem_value", "max_elem_value", "content_level", "color"]].copy()
            levels = []
            colors = []

            for _, field_row in field.iterrows():
                value = field_row[element_name_in_fields]

                for _, row in element_data.iterrows():
                    if row["min_elem_value"] <= value <= row["max_elem_value"]:
                        levels.append(row["content_level"])
                        colors.append(row["color"])
                        break

            field[f"{element_name_in_fields}_level"] = levels
            field[f"{element_name_in_fields}_color"] = colors

        return field

    def search_recommendation_data(self, user_id, field_name):
        """
        Searches for recommendation data for a specific field of a specific user.
        """
        self.cur.execute(
            """
                SELECT recommendation
                FROM recommendation 
                WHERE user_id = %s AND field_name = %s
            """,
            (user_id, field_name),
        )
        result = self.cur.fetchall()

        if not result:
            return None

        all_recommendations = []

        for (recommendation,) in result:
            df = pd.DataFrame(recommendation)
            df["field_name"] = field_name
            all_recommendations.append(df)

        return pd.concat(all_recommendations, ignore_index=True)

    def format_data(self, user_id, field_name):
        """
        Merges field data with its recommendation and assigns the appropriate color
        to the soil chemical analysis values.
        """
        recommendation = self.search_recommendation_data(user_id, field_name)
        field = self.search_field_data(user_id, field_name)

        if field is None:
            return None

        if recommendation is None:
            return self.color_grade_chem_level(field)
        recommendation = recommendation.drop_duplicates(
            subset=["field_name", "zone_name"]
        )
        merged = pd.merge(
            field,
            recommendation,
            on=["field_name", "zone_name"],
            how="left",
        )

        merged = self.color_grade_chem_level(merged)

        return merged

    def get_user_fields_list(self, user_id):
        """
        Gets a list of all user fields and farms for the Your Fields Page.
        """

        self.cur.execute(
            """
                SELECT farm_name, field_name
                FROM field_data
                WHERE user_id = %s
            """,
            (user_id,),
        )
        result = self.cur.fetchall()

        field_list = []
        if result:
            for row in result:
                field_list.append({"farm_name": row[0], "field_name": row[1]})
        else:
            field_list = []

        return field_list
