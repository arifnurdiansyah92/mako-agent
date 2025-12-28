-- DROP SCHEMA public;

CREATE SCHEMA public AUTHORIZATION pg_database_owner;

-- Drop table

-- DROP TABLE public.ingredients;

CREATE TABLE public.ingredients (
	id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	"name" text NOT NULL,
	CONSTRAINT ingredients_name_key UNIQUE (name),
	CONSTRAINT ingredients_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_ingredients_name ON public.ingredients USING btree (name);

-- Drop table

-- DROP TABLE public.recipe_ingredients;

CREATE TABLE public.recipe_ingredients (
	id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	recipe_id int8 NULL,
	ingredient_id int8 NULL,
	amount text NOT NULL,
	CONSTRAINT recipe_ingredients_pkey PRIMARY KEY (id),
	CONSTRAINT recipe_ingredients_recipe_id_ingredient_id_key UNIQUE (recipe_id, ingredient_id),
	CONSTRAINT recipe_ingredients_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE,
	CONSTRAINT recipe_ingredients_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE
);
CREATE INDEX idx_recipe_ingredients_recipe_id ON public.recipe_ingredients USING btree (recipe_id);

-- Drop table

-- DROP TABLE public.recipe_steps;

CREATE TABLE public.recipe_steps (
	id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	recipe_id int8 NULL,
	step_number int4 NOT NULL,
	description text NOT NULL,
	CONSTRAINT recipe_steps_pkey PRIMARY KEY (id),
	CONSTRAINT recipe_steps_recipe_id_step_number_key UNIQUE (recipe_id, step_number),
	CONSTRAINT recipe_steps_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE
);
CREATE INDEX idx_recipe_steps_recipe_id ON public.recipe_steps USING btree (recipe_id);

-- Drop table

-- DROP TABLE public.recipes;

CREATE TABLE public.recipes (
	id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	"name" text NOT NULL,
	link text NULL,
	image_url text NULL,
	calories int4 NOT NULL,
	protein numeric(5, 1) NOT NULL,
	fat numeric(5, 1) NOT NULL,
	carbs numeric(5, 1) NOT NULL,
	created_at timestamptz DEFAULT now() NULL,
	updated_at timestamptz DEFAULT now() NULL,
	CONSTRAINT recipes_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_recipes_name ON public.recipes USING btree (name);