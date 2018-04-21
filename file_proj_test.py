from final_proj import *
import unittest


class testRecipeSearch(unittest.TestCase):

    def testCategory(self):

        test = getRecipeCategory()
        temp_list = []
        for item in test:
            temp_list.append(item['name'])

        self.assertIn('Meal Type', temp_list)




if __name__ == '__main__':
    unittest.main()
