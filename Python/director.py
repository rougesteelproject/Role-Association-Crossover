#TODO replace exceptions with traceback.print_exc()

#   functions modify lists, so we don't neet to return them. 

#TODO a page with everybody, alphabetically

#TODO a way to add user-made roles to replace the ... or 'additional voices' for actorw w/ multiple roles, like in skyrim

#TODO commit should be up to db_cont

import distutils
import distutils.util
from urllib import request

from page_generators.page_generator_sql import PageGeneratorSQL

class Director:
    def __init__(self, db_type : str = 'sql'):
        self._db_type = db_type
        
        self._create_db_controller()
        self._import_page_generator()

    def _create_db_controller(self):
        if self._db_type == 'sql':
            from db_controllers.db_cont_sql import DatabaseControllerSQL
            self._db_control = DatabaseControllerSQL()

    def _import_page_generator(self):
        if self._db_type == 'sql':
            from page_generators.page_generator_sql import PageGeneratorSQL

    def _generate_page(self, layers_to_generate, enable_actor_swap = False, base_actor = None, base_mr = None):
        page_generator = PageGeneratorSQL(layers_to_generate=layers_to_generate, callback_get_actor=self._db_control.get_actor, callback_get_mr=self._db_control.get_mr, enable_actor_swap=enable_actor_swap, base_actor=base_actor, base_mr=base_mr)

        page_generator.generate_content()

        return page_generator

    def run_flask(self, **kwargs):
        from flask_wrapper import FlaskWrapper

        self._flask_wrapper = FlaskWrapper()

        self._add_flask_endpoints()

        self._flask_wrapper.run(**kwargs)

    def import_imdb(self):
        from IMDB_importer import IMDBImporter as IMDBimp

        self._IMDB_importer = IMDBimp(callback_create_actor = self._db_control.create_actor, callback_create_role = self._db_control.create_role, callback_create_mr = self._db_control.create_mr)

        self._IMDB_importer.get_all_IMDB()

        self._db_control.commit()

    def _add_flask_endpoints(self):
        
        #index
        #TODO generate featured articles based off of hits or connections (after the webview/ hub sigils works)
        self._flask_wrapper.add_endpoint(endpoint= '/', endpoint_name= 'index', handler= self._route_index)

        #wiki
        self._flask_wrapper.add_endpoint(endpoint= '/wiki', endpoint_name= 'wiki', handler = self._route_wiki, methods= ['GET', 'POST'])

        #actor editor
        self._flask_wrapper.add_endpoint(endpoint= '/editor/actor', endpoint_name= 'actor_editor', handler=self._route_actor_editor, methods=['GET','POST'])

        #mr editor
        self._flask_wrapper.add_endpoint(endpoint='/editor/meta/', endpoint_name='mr_editor', handler=self._route_mr_editor, methods=['GET','POST'])

        #role editor
        self._flask_wrapper.add_endpoint(endpoint= '/editor/role', endpoint_name= 'role_editor', handler = self._route_role_editor, methods=['GET','POST'])

        #character connector
        self._flask_wrapper.add_endpoint(endpoint='/character_connector', endpoint_name='character_connector', handler = self._route_character_connector, methods=['GET', 'POST'])

        #web view
        self._flask_wrapper.add_endpoint(endpoint='/webview', endpoint_name='webview', handler= self._route_webview)

        #submit image
        self._flask_wrapper.add_endpoint(endpoint='/submit_image', endpoint_name='submit_image', handler=self._route_submit_image,methods=['POST'])

        #search
        self._flask_wrapper.add_endpoint(endpoint='/search', endpoint_name='search', handler=self._route_search)

        #edit ability
        self._flask_wrapper.add_endpoint(endpoint='/editor/ability', endpoint_name = 'ability_editor', handler = self._route_ability_editor,methods=['POST','GET'])

        #edit template
        self._flask_wrapper.add_endpoint(endpoint='/editor/template', endpoint_name='template_editor', handler=self._route_template_editor, methods=['POST', 'GET'])

        #create template
        self._flask_wrapper.add_endpoint(endpoint='/create_template', endpoint_name='create_template', handler=self._route_create_template, methods=['POST', 'GET'])

        #create_ability
        self._flask_wrapper.add_endpoint(endpoint='/create_ability', endpoint_name='create_ability', handler=self._route_create_ability, methods=['POST', 'GET'])

    def _route_index(self):
        return self._flask_wrapper.render()

    def _route_wiki(self):
        #?my_var=my_value

        request = self._flask_wrapper.request().args

        base_actor = None
        base_mr = None

        level = int(request['level'])
        base_id = request['base_id']
        base_is_actor = bool(distutils.util.strtobool(request['base_is_actor']))
        if "enable_actor_swap" in request:
            enable_actor_swap = True
        else:
            enable_actor_swap = False
        print(f'director: id to fetch: {base_id}')

        if base_is_actor:
            base_actor = self._db_control.get_actor(base_id)
        else:
            base_mr = self._db_control.get_mr(base_id)
        
        #TODO there's probably a way to send a dictionary or something instead of the generator itself.
        
        generator = self._generate_page(base_id, level, self._db_control, enable_actor_swap, base_actor, base_mr)
        return self._flask_wrapper.render('wiki_template.html', generator=generator, blurb_editor_link="", hub_sigils="" )
       
    def _route_actor_editor(self):

        request = self._flask_wrapper.request()

        if request.method == 'POST':

            editorID = request.form['editorID']
            goBackUrl = request.form['goBackUrl']

            if "bio_editor" in request.form:
                new_bio  = request.form['bio']

                #gets the old desc, plops it into history, then replaces it with the new
                self._db_control.create_actor_history(editorID,new_bio)
                self._db_control.commit()

            if "history_reverter" in request.form:
                new_bio  = request.form['bio']
                
                self._db_control.create_actor_history(editorID,new_bio)
                self._db_control.commit()

            if "ability_remover" in request.form:
                abilities_to_remove = request.form.getlist('remove_ability')
                self._db_control.remove_ability_actor(editorID, abilities_to_remove)
                self._db_control.commit()

            if "ability_adder" in request.form:
                abilities_to_add = request.form.getlist('add_ability')
                self._db_control.add_ability_actor(editorID, abilities_to_add)
                self._db_control.commit()

            if "relationship_adder" in request.form:
                actor1_id =request.form['actor1_id']
                actor1_name = request.form['actor1_name']
                actor2_id, actor2_name = request.form['actor2'].split('|')
                type = request.form['relationship_type']
                self._db_control.add_relationship_actor(actor1_id,actor1_name,actor2_id, actor2_name, type)
                self._db_control.commit()

            if "relationship_remover" in request.form:
                relationship_ids = request.form.getlist('remove_relationship')
                self._db_control.remove_relationships_actor(relationship_ids)
                self._db_control.commit()
                
        else:
            editorID = request.args['editorID']
            goBackUrl = request.referrer
            
            #a list of all histry entries

        actor = self._db_control.get_actor(editorID)
        history = self._db_control.get_actor_history(editorID)
        abilities_that_are_not_connected = self._db_control.get_ability_list_exclude_actor(actor.id)

        all_actors = self._db_control.get_all_actors()

        return self._flask_wrapper.render('actor_editor.html', goBackUrl=goBackUrl, actor=actor, history=history, abilities_that_are_not_connected=abilities_that_are_not_connected, all_actors=all_actors)

    def _route_mr_editor(self):

        request = self._flask_wrapper.request()

        #WHen the user presses 'Submit'
        if request.method == 'POST':
            new_description  = request.form['description']
            editorID = request.form['editorID']
            goBackUrl = request.form['goBackUrl']
            #gets the old desc, plops it into history, then replaces it with the new
            self._db_control.create_mr_history(editorID,new_description)
            self._db_control.commit()
            self._flask_wrapper.redirect(goBackUrl)
        else:
            editorID = request.args['editorID']
            goBackUrl = request.referrer
            history = self._db_control.get_mr_history(editorID)
            #a list of all histry entries

            mr = self._db_control.get_mr(editorID)

            return self._flask_wrapper.render('mr_editor.html', goBackUrl=goBackUrl, mr=mr, history=history)

    def _route_role_editor(self):
        #When the user presses 'Submit'

        request = self._flask_wrapper.request()

        if request.method == 'POST':
            editorID = request.form['editorID']
            goBackUrl = request.form['goBackUrl']
            
            if "description_editor" in request.form:
                new_description  = request.form['description']
                alignment = request.form['alignment']
                alive_or_dead = request.form['alive_or_dead']
                #gets the old desc, plops it into history, then replaces it with the new
                self._db_control.create_role_history(editorID,new_description, alive_or_dead, alignment)
                self._db_control.commit()

            if "history_reverter" in request.form:
                new_description  = request.form['description']
                alignment = request.form['alignment']
                alive_or_dead = request.form['alive_or_dead']
                self._db_control.create_role_history(editorID,new_description, alive_or_dead, alignment)
                self._db_control.commit()

            if "ability_remover" in request.form:
                abilities_to_remove = request.form.getlist('remove_ability')
                self._db_control.remove_ability_role(editorID, abilities_to_remove)
                self._db_control.commit()

            if "ability_adder" in request.form:
                abilities_to_add = request.form.getlist('add_ability')
                self._db_control.add_ability_role(editorID, abilities_to_add)
                self._db_control.commit()

            if "template_adder" in request.form:
                templates_to_add = request.form.getlist('add_template')
                self._db_control.add_template_role(editorID, templates_to_add)
                self._db_control.commit()

            if "ability_template_remover" in request.form:
                templates_to_remove = request.form.getlist('remove_template')
                self._db_control.remove_template(editorID, templates_to_remove)
                self._db_control.commit()

            if "relationship_adder" in request.form:
                role1_id =request.form['role1_id']
                role1_name = request.form['role1_name']
                role2_id, role2_name = request.form['role2'].split('|')
                type = request.form['relationship_type']
                self._db_control.add_relationship_role(role1_id,role1_name,role2_id, role2_name, type)
                self._db_control.commit()

            if "relationship_remover" in request.form:
                relationship_ids = request.form.getlist('remove_relationship')
                self._db_control.remove_relationships_role(relationship_ids)
                self._db_control.commit()

        else:
            editorID = request.args['editorID']
            goBackUrl = request.referrer
        
        history = self._db_control.get_role_history(editorID)
        #a list of all histry entries

        role = self._db_control.get_role(editorID)

        abilities_that_are_not_connected = self._db_control.get_ability_list_exclude_role(role.id)
        ability_templates_that_are_not_connected = self._db_control.get_ability_template_list_exclude_role(role.id)

        all_roles = self._db_control.get_all_roles()

        return self._flask_wrapper.render('role_editor.html', goBackUrl=goBackUrl, role=role, history=history, abilities_that_are_not_connected=abilities_that_are_not_connected, ability_templates_that_are_not_connected=ability_templates_that_are_not_connected,all_roles=all_roles)
        
    def _route_character_connector(self):

        request = self._flask_wrapper.request()

        if "search-submit" in request.form:

            #TODO make this drag and drop?
            name_1 = request.form['name_1']
            name_2 = request.form['name_2']
            connector_mrs, connector_mrs2 = self._db_control.search_char_connector(name_1, name_2)

            self._flask_wrapper.render('character_connector.html',have_results=True, connector_mrs=connector_mrs, connector_mrs2=connector_mrs2, name_1=name_1, name_2=name_2)

        if "matcher-submit" in request.form:
            id1 = request.form['id1']
            id2 = request.form['id2']
            mode = request.form['mode']

            self._db_control.character_connector_switch(mode,id1,id2)

            name_1 = request.form['name_1']
            name_2 = request.form['name_2']
            connector_mrs, connector_mrs2 = self._db_control.search_char_connector(name_1, name_2)

            self._flask_wrapper._render('character_connector.html', have_results=True ,connector_mrs=connector_mrs, connector_mrs2=connector_mrs2, name_1=name_1, name_2=name_2)
        
        return self._flask_wrapper._render('character_connector.html', have_results = False)

    def _route_webview(self):
        return self._flask_wrapper._render('webview.html')

    def _route_submit_image(self):
        request = self._flask_wrapper.request()

        page_type=request.form['typeImg']
        page_id = request.form['IDImg'] 
        caption = request.form['caption']
        uploaded_file = request.files['file']
        go_back_url = request.form['goBackUrlImg']
        
        if uploaded_file.filename != '':
            uploaded_file.save('static/' + uploaded_file.filename)

        self._db_control.add_image(page_type, page_id, uploaded_file.filename, caption)

        #TODO this needs to stay on the same page, instead
            #a form with stay_here url or something (request.referer?)
        return self._flask_wrapper.redirect(go_back_url)       

    def _route_search(self):
        request = self._flask_wrapper.request()

        query = request.args['query']
        search_actors, search_mrs = self._db_control.search_bar(query)

        return self._flask_wrapper.render('search.html', search_mrs = search_mrs, search_actors = search_actors)

    def _route_ability_editor(self):
        
        request = self._flask_wrapper.request()

        if request.method == 'POST':
            ability_id = request.form['editorID']
            goBackUrl = request.form['goBackUrl']
            
            if "edit_ability" in request.form:
                new_description  = request.form['description']
                new_name = request.form['name']

                self._db_control.create_ability_history(ability_id, new_name,new_description)
                self._db_control.commit()

            if "history_reverter" in request.form:
                new_name = request.form['name']
                new_description  = request.form['description']

                self._db_control.create_ability_history(ability_id, new_name,new_description)
                self._db_control.commit()

        else: 
            goBackUrl = request.referrer
            ability_id = request.args['id']
        
        ability = self._db_control.get_ability(ability_id)
        history = self._db_control.get_ability_history(ability_id)
        return self._flask_wrapper.render('ability_editor.html',ability=ability, history=history, goBackUrl=goBackUrl)

    def _route_template_editor(self):
        request = self._flask_wrapper.request()

        if request.method == 'POST':
            template_id = request.form['editorID']
            goBackUrl = request.form['goBackUrl']
            
            if "edit_template" in request.form:
                new_description  = request.form['description']
                new_name = request.form['name']

                self._db_control.create_template_history(template_id, new_name,new_description)
                self._db_control.commit()

            if "history_reverter" in request.form:
                new_name = request.form['name']
                new_description  = request.form['description']

                self._db_control.create_template_history(template_id, new_name,new_description)
                self._db_control.commit()

            if "ability_remover" in request.form:
                abilities_to_remove = request.form.getlist('remove_ability')
                self._db_control.remove_ability_from_template(template_id, abilities_to_remove)
                self._db_control.commit()

            if "ability_adder" in request.form:
                abilities_to_add = request.form.getlist('add_ability')
                self._db_control.add_abilities_to_template(template_id,abilities_to_add)
                self._db_control.commit() 

        else: 
            goBackUrl = request.referrer
            template_id = request.args['id']
        
        abilities_that_are_not_connected = self._db_control.get_ability_list_exclude_template(template_id)
        template = self._db_control.get_ability_template(template_id)
        history = self._db_control.get_template_history(template_id)
        return self._flask_wrapper.render('template_editor.html',template=template, abilities_that_are_not_connected=abilities_that_are_not_connected ,history=history, goBackUrl=goBackUrl)

    def _route_create_template(self):
        request = self._flask_wrapper.request()

        if "create_template" in request.form:
            name = request.form['name']
            description = request.form['description']
            goBackUrl = request.form['goBackUrl']
            
            template_id = self._db_control.create_ability_template(name, description)
            self._db_control.commit()

            template = self._db_control.get_ability_template(template_id)
            history = self._db_control.get_template_history(template_id)
            abilities_that_are_not_connected = self._db_control.get_ability_list_exclude_template(template_id)

            #TODO this needs to redirect so it sends the values to temp_editor, while go_back still works
            return self._flask_wrapper.render('template_editor.html', template=template, abilities_that_are_not_connected=abilities_that_are_not_connected, history=history, goBackUrl=goBackUrl)
        else:
            goBackUrl = request.referrer
            return self._flask_wrapper.render('create_template.html', goBackUrl=goBackUrl)

    def _route_create_ability(self):
        request = self._flask_wrapper.request()

        if "create_ability" in request.form:
            name = request.form['name']
            description = request.form['description']
            goBackUrl = request.form['goBackUrl']

            ability_id = self._db_control.create_ability(name, description)
            
            ability = self._db_control.get_ability(ability_id)
            history = self._db_control.get_ability_history(ability_id)

            return self._flask_wrapper.render('ability_editor.html', ability=ability, history=history, goBackUrl=goBackUrl)
            
            #create the ability using db_cont, then go to ability_editor
        else:
            goBackUrl = request.referrer
            #render the template with the form (the normal response to this link)
            return self._flask_wrapper.render('create_ability.html', goBackUrl=goBackUrl)

#TODO an arror page if an actor does not exist in imdb

def main():
    db_type = 'sql'
    director = Director(db_type=db_type)
    #director.import_imdb()
    director.run_flask(port=5000)

if __name__ == '__main__':
    main()
