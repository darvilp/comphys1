#include "wavepacket.hpp"

class Wavepacket : public WavepacketBase {
public:
  // define names for complex numbers and vectors
  typedef complex<double> cdouble;
  typedef Matrix<cdouble,1> cvector;

  Wavepacket( int iN=128, double iL=100, double idt=0.1, bool iper=true ) : 
    WavepacketBase( iN, iL, idt, iper ), chi(iN), a(iN), b(iN), c(iN)
  {

    // elements of tridiagonal matrix Q = (1/2)(1 + i dt H / (2 hbar))
    const cdouble i(0.0, 1.0);
    for (int j = 0; j < N; j++) {
      a[j] = - i * dt * h_bar / (8 * mass * dx * dx);
      b[j] = 0.5 + 1j * dt / (4 * h_bar) *
	(V(x[j]) + h_bar * h_bar / (mass * dx * dx));
      c[j] = a[j];
    }
    alpha = c[N-1];
    beta = a[0];

  }

  cvector solve_tridiagonal(cvector& a, cvector& b, cvector& c, cvector& r) {
    // solve Ax = r where A is tridiagonal with diagonals (a, b, c) and return x
    int n = r.size();
    cvector x(n), gama(n);
    cdouble beta = b[0];
    x[0] = r[0] / beta;
    for (int j = 1; j < n; j++) {
      gama[j] = c[j-1] / beta;
      beta = b[j] - a[j] * gama[j];
      x[j] = (r[j] - a[j] * x[j-1]) / beta;
    }
    for (int j = n-2; j >= 0; j--)
      x[j] -= gama[j+1] * x[j+1];
    return x;
  }

  cvector solve_tridiagonal_cyclic(
				   cvector& a, cvector& b, cvector& c, cvector& r,
				   complex<double> alpha, complex<double> beta)
  {
    // solve Ax = r where A is tridagonal with corner elements alpha, beta
    int n = r.size();
    cvector x(n), b_prime(n), u(n), z(n);
    cdouble gama = -b[0];
    b_prime[0] = b[0] - gama;
    b_prime[n-1] = b[n-1] - alpha * beta / gama;
    for (int j = 1; j < n; j++)
      b_prime[j] = b[j];
    x = solve_tridiagonal(a, b_prime, c, r);
    u[0] = gama;
    u[n-1] = alpha;
    for (int j = 1; j < n-1; j++)
      u[j] = 0;
    z = solve_tridiagonal(a, b_prime, c, u);
    cdouble fact = x[0] + beta * x[n-1] / gama;
    fact /= 1.0 + z[0] + beta * z[n-1] / gama;
    for (int j = 0; j < n; j++)
      x[j] -= fact * z[j];
    return x;
  }

  void take_step () {              // time step using sparse matrix routines
    if (periodic)
      chi = solve_tridiagonal_cyclic(a, b, c, psi, alpha, beta);
    else
      chi = solve_tridiagonal(a, b, c, psi);
    for (int j = 0; j < N; j++)
      psi[j] = chi[j] - psi[j];
    t += dt;

  }

protected : 
  cvector chi;                    // complex wavefunction
  cvector a, b, c;                // to represent tridiagonal elements of Q
  cdouble alpha, beta;            // corner elements of Q


};



int main()
{


  cout << " Quantum Wavepacket Motion" << endl;
  Wavepacket wavepacket;
  cout << "Got a wavepacket" << endl;

  ofstream file("potential.data");
  for (int i = 0; i < wavepacket.get_N(); i++)
    file << wavepacket.get_x(i) << '\t' << wavepacket.V(wavepacket.get_x(i) ) << '\n';
  file.close();
  cout << " saved V(x) in file potential.data" << endl;



#ifdef _WIN32
  ostringstream pyout;
  pyout << "env python.exe animator_for_cpp.py " << wavepacket.get_N();
  FILE *pypipe = _popen(pyout.str().c_str(), "w");
#else
  ostringstream pyout;
  pyout << "/usr/bin/env python animator_for_cpp.py " << wavepacket.get_N();
  FILE *pypipe = popen(pyout.str().c_str(), "w");
#endif


  wavepacket.save_psi(0);
  int plots = 10;
  for (int plot = 1; plot <= plots; plot++) {
    cout << "plot = " << plot << endl;
    double delta_t = 0;
    while (delta_t < wavepacket.get_L() / (plots * wavepacket.get_velocity())) {
      wavepacket.take_step();
      delta_t += wavepacket.get_dt();
    }
    wavepacket.save_psi(plot);
  }

  
  // simple Mpl pipes animation
  cout << " Enter animation time: ";
  double t_max;
  cin >> t_max;
  wavepacket = Wavepacket();
  double frame_rate = 30;
  double dt_frame = 1 / frame_rate;
  int steps_per_frame = max(1, int(dt_frame /   wavepacket.get_dt()));

  while (wavepacket.get_t() < t_max) {
    ostringstream os;
    for (int i = 0; i < wavepacket.get_N(); i++)
      os << std::abs(wavepacket.get_psi()[i]) << ',';
    fprintf(pypipe, "%s\n", os.str().c_str());
    fflush(pypipe);
    time_t start_time = clock();
    for (int step = 0; step < steps_per_frame; step++) {
      wavepacket.take_step();
    }
    while (true) {
      double secs = (clock() - start_time) / double(CLOCKS_PER_SEC);
      if (secs > dt_frame)
	break;
    }
  }
  fclose(pypipe);
}




