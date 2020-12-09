#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <iostream>
// TODO: DEPENDENCIES WITH THE PROJECT

void framebuffer_size_callback(GLFWwindow window, int width, int height);

void processInput(GLFWwindow* window)
{
	if(glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS)
	{
		glfwSetWindowShouldClose(window, true);
	}
}

int main(){
	glfwInit();
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);


	GLFWwindow* window = glfwCreateWindow(800, 600,"learn opengl",nullptr,nullptr);
	if(window == nullptr)
	{
		std::cout << "fail"<< std::endl;
		glfwTerminate();
		return -1;
	}
	glfwMakeContextCurrent(window);
	//glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
	
	// GLAD manages the function pointers to opengl, to initialize it we do: 
	if(!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
	// we pass to GLAD the function to load the address of OPENGL function pointers
	// GLFW has a function glfwProcAddress which gives the correct function for that
	{
		std::cout << "failed to load glad" << std::endl;
		return -1;
	}

	//this tells opengl the size of the rendering window
	// (location lower left cornet of the window, width and height of the rendering window in pixels)
	glViewport(0,0,800,600);
	// coordinates in opengl are between -1 and 1. so mapping 0,800 to -1,1.
	
	// render loop
	while(!glfwWindowShouldClose(window))
	{
		processInput(window);

		glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
		glClear(GL_COLOR_BUFFER_BIT);

		glfwSwapBuffers(window);
		glfwPollEvents();
	}

	glfwTerminate();
	return 0;

}

void framebuffer_size_callback(GLFWwindow* window, int width, int height)
{
	glViewport(0,0, width, height);
}
