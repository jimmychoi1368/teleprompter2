from pythonforandroid.recipe import Recipe
from pythonforandroid.recipes.libffi import LibffiRecipe

class CustomLibffiRecipe(LibffiRecipe):
    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # 设置一些环境变量来避免autoconf错误
        env['ACLOCAL_FLAGS'] = '-I /usr/share/aclocal'
        return env

# 注册自定义的libffi配方
def get_custom_recipes():
    return {'libffi': CustomLibffiRecipe}

