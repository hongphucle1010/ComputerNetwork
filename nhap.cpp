#include <iostream>
#include <string>
using namespace std;


int main() {
    for (int i=2024; i>=1950; i--) {
        cout<<"<option>"<<i<<"</option> ";
        if (i%5==0) cout<<endl;
    }
}