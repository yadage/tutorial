#include <iostream>
#include <fstream>

int main(int argc, char** argv) {
  std::ofstream myfile;
  std::cout << "Hello World. We will write this message: " << argv[1] << std::endl;
  myfile.open(argv[2]);
  myfile << "Hello, the message was: " << argv[1] << std::endl;
  myfile.close();
  std::cout << "Done! try looking into " << argv[2] << std::endl;
  return 0;
}
