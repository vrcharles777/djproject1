from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from selenium.common.exceptions import NoSuchElementException

class MySeleniumTests(StaticLiveServerTestCase):
    # carregar una BD de test
    #fixtures = ['testdb.json',]
 
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)

        # Crea un superusuario
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()
 
    @classmethod
    def tearDownClass(cls):
        # tanquem browser
        # comentar la propera línia si volem veure el resultat de l'execució al navegador
        #cls.selenium.quit()
        super().tearDownClass()
 
    def test_login(self):
        # anem directament a la pàgina d'accés a l'admin panel
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
 
        # comprovem que el títol de la pàgina és el que esperem
        self.assertEqual( self.selenium.title , "Log in | Django site admin" )
 
        # introduïm dades de login i cliquem el botó "Log in" per entrar
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('isard')
        password_input = self.selenium.find_element(By.NAME,"password")
        password_input.send_keys('pirineus')
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()
 
        # testejem que hem entrat a l'admin panel comprovant el títol de la pàgina
        self.assertEqual( self.selenium.title , "Site administration | Django site admin" )        

        try:
            self.selenium.find_element(By.XPATH, "//button[text()='Log outt']")
            assert False, "El elemento 'Log outt' fue encontrado cuando NO debería estar presente."
        except NoSuchElementException:
            pass  # El elemento no está, así que la prueba pasa sin errores

        # Busca el botón "View site" y verifica que está presente
        try:
            view_site_button = self.selenium.find_element(By.XPATH, "//a[text()='VIEW SITE']")
        except NoSuchElementException:
            self.fail("El botón 'View site' no se encontró en la página de administración.")
        
        # Hace clic en el botón "View site" y verifica que la página cargue correctamente
        view_site_button.click()
        
        # Cambia a la nueva pestaña o ventana que se haya abierto
        self.selenium.switch_to.window(self.selenium.window_handles[-1])

        # Verifica que la URL de la página cargada no tenga un código de error HTTP
        current_url = self.selenium.current_url
        response = self.selenium.get(current_url)
        
        self.assertEqual(response.status_code, 200, "La página redirigida no es válida.")