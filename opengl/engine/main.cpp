#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <iostream>
// TODO: DEPENDENCIES WITH THE PROJECT

void framebuffer_size_callback(GLFWwindow window, int width, int height);

const char *vertexShaderSource =
		"	#version 330 core																			\n"
    "	layout (location = 0) in vec3 aPos;										\n"
    "	void main()																						\n"
    "	{																											\n"
    "	   gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);		\n"
    "	}																											\0";
const char* fragmentShaderSource = 
"#version 330 core \n"
"out vec4 FragColor; \n"
"void main() \n"
"{ \n"
"    FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);\n"
"}\0 ";


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

	// ------ vertex shader

	unsigned int vertexShader;
	vertexShader = glCreateShader(GL_VERTEX_SHADER);
	// attach shader source code to shader object and compile the shader	
	// (object to compile to as its argument, how many strings as source code, source code)
	glShaderSource(vertexShader, 1, &vertexShaderSource, nullptr);
	glCompileShader(vertexShader);
	
	int success;
	char infoLog[512];
	glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success );

	if(!success)
	{
		glGetShaderInfoLog(vertexShader, 512, nullptr, infoLog);
		std::cout<< "error shader compilation" << infoLog << std::endl;
	}

	// ------ fragment shader
	unsigned int fragmentShader;
	fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
	glShaderSource(fragmentShader, 1, &fragmentShaderSource, nullptr);
	glCompileShader(fragmentShader);

	// ----- shader program object
	unsigned int shaderProgram;
	shaderProgram = glCreateProgram();

	glAttachShader(shaderProgram, vertexShader);
	glAttachShader(shaderProgram, fragmentShader);
	glLinkProgram(shaderProgram);

	
	// dont need the shaders anymore
	glDeleteShader(vertexShader);
	glDeleteShader(fragmentShader);



	// ------- vertices and buffer

	float vertices[] = {
		-0.5f, -0.5f, 0.0f,
		0.5f, -0.5f, 0.0f,
		0.0f, 0.5f, 0.0f,
	};

	unsigned int VBO, VAO;
	glGenVertexArrays(1, &VAO);
	glGenBuffers(1, &VBO);
	// bind the Vertex Array Object first, then bind and set vertex buffer(s), and then configure vertex attributes(s).
	glBindVertexArray(VAO);

	glBindBuffer(GL_ARRAY_BUFFER, VBO);
	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void*)0);
	glEnableVertexAttribArray(0);

	// note that this is allowed, the call to glVertexAttribPointer registered VBO as the vertex attribute's bound vertex buffer object so afterwards we can safely unbind
	glBindBuffer(GL_ARRAY_BUFFER, 0); 

	// You can unbind the VAO afterwards so other VAO calls won't accidentally modify this VAO, but this rarely happens. Modifying other
	// VAOs requires a call to glBindVertexArray anyways so we generally don't unbind VAOs (nor VBOs) when it's not directly necessary.
	glBindVertexArray(0); 


	// uncomment this call to draw in wireframe polygons.
	//glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);

	while(!glfwWindowShouldClose(window))
	{
		processInput(window);

		glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
		glClear(GL_COLOR_BUFFER_BIT);

		// draw
		// draw our first triangle
		glUseProgram(shaderProgram);
		glBindVertexArray(VAO); // seeing as we only have a single VAO there's no need to bind it every time, but we'll do so to keep things a bit more organized
		glDrawArrays(GL_TRIANGLES, 0, 3);

		glfwSwapBuffers(window);
		glfwPollEvents();
	}

	glDeleteVertexArrays(1, &VAO);
	glDeleteBuffers(1, &VBO);
	glDeleteProgram(shaderProgram);

	glfwTerminate();
	return 0;

}

void framebuffer_size_callback(GLFWwindow* window, int width, int height)
{
	glViewport(0,0, width, height);
}
