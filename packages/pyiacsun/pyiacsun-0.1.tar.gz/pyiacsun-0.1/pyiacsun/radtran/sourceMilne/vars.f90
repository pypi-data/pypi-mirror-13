!********************************************************
! Global variables
!********************************************************
module vars
implicit none

	real(kind=8), parameter :: PK = 1.3806503d-16, UMA = 1.66053873d-24, PC = 2.99792458d10
	real(kind=8), parameter :: PH = 6.62606876d-27, PHK = PH / PK, PHC = 2.d0 * PH / PC**2
	real(kind=8), parameter :: PME = 9.10938188d-28, PE = 4.8032d-10, PI = 3.14159265359d0
	real(kind=8), parameter :: PHC2 = 2.d0 * PH * PC**2, OPA = PI * PE**2 / (PME * PC)
	real(kind=8), parameter :: SQRTPI = 1.77245385091d0, EARTH_SUN_DISTANCE = 1.495979d13
	real(kind=8), parameter :: LARMOR = PE/(4.d0*PI*PME*PC), PMP = 1.67262158d-24
	real(kind=8), parameter :: NUCLEAR_MAGNETON = PE*PH/(2.d0*PI*PMP)
	real(kind=8), parameter :: BOHR_MAGNETON = PE*PH/(2.d0*PI*PME)
	real(kind=8), parameter :: PH2C3 = 2.d0 * PH**2 * PC**3, PERTURBATION = 0.005d0	
	
	real(kind=8), allocatable :: zeeman_voigt(:,:), zeeman_faraday(:,:)
		
	type stokes_type
		integer :: nlambda
		real(kind=8), pointer :: stokes(:,:), lambda(:), sigma(:,:)
	end type stokes_type
	
	type modelo_type
		real(kind=8) :: Bfield, theta, chi, vmac, damping, B0, B1, mu, doppler, kl
	end type modelo_type
		
	type line_type
		character(len=2) :: theory
		integer :: nLambda
		real(kind=8) :: lambdaInit, lambdaStep, lambda
		real(kind=8) :: wave0, Jup, Jlow, gup, glow		
	end type line_type
	
	type(stokes_type) :: Observation, Emergent, Stokes_unperturbed, Stokes_perturbed
	type(stokes_type) :: Stokes_Syn
	
	type(modelo_type) :: model
	type(line_type) :: line(10)
	integer :: nLines
	
	real(kind=8), allocatable :: ki(:), kq(:), ku(:), kv(:), fq(:), fu(:), fv(:), stokes(:,:), delta(:)
	real(kind=8), allocatable :: ki_partial(:), kq_partial(:), ku_partial(:), kv_partial(:)
	real(kind=8), allocatable :: fq_partial(:), fu_partial(:), fv_partial(:)
	
	real(kind=8), allocatable :: profile(:,:), v(:)
				
end module vars
