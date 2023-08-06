module pyHazelMod
use iso_c_binding, only: c_int, c_double
use vars
use maths
use io
use SEE
use rt_coef
use synth
use allen
implicit none

contains
subroutine c_hazel(synModeInput, nSlabsInput, B1Input, B2Input, hInput, tau1Input, tau2Input, boundaryInput, &
	transInput, atomicPolInput, anglesInput, nLambdaInput, lambdaAxisInput, dopplerWidthInput, dopplerWidth2Input, dampingInput, &
	dopplerVelocityInput, dopplerVelocity2Input, ffInput, betaInput, nbarInput, omegaInput, &
	wavelengthOutput, stokesOutput, epsOutput, etaOutput) bind(c)

	integer(c_int), intent(in) :: synModeInput, nSlabsInput, transInput, atomicPolInput
	integer(c_int), intent(in) :: nLambdaInput
	real(c_double), intent(in), dimension(nLambdaInput) :: lambdaAxisInput
	real(c_double), intent(in), dimension(3) :: B1Input, anglesInput
	real(c_double), intent(in), dimension(3) :: B2Input
	real(c_double), intent(in), dimension(4) :: boundaryInput
	real(c_double), intent(in):: tau2Input, dopplerWidth2Input, dopplerVelocity2Input, ffInput
	real(c_double), intent(in), dimension(4) :: nbarInput, omegaInput
	real(c_double), intent(in) :: hInput, tau1Input, dopplerWidthInput, dampingInput, dopplerVelocityInput, betaInput
	real(c_double), intent(out), dimension(nLambdaInput) :: wavelengthOutput
	real(c_double), intent(out), dimension(4,nLambdaInput) :: stokesOutput
	real(c_double), intent(out), dimension(4,nLambdaInput) :: epsOutput
	real(c_double), intent(out), dimension(4,4,nLambdaInput) :: etaOutput
	
	integer :: n, nterml, ntermu
	
	real(c_double) :: ae, wavelength, reduction_factor, reduction_factor_omega, j10
	integer :: i, j
		
! Initialize the random number generator
! 	call random_seed
		
! Initialize Allen's data
! 	call read_allen_data
		
! Fill the factorial array
! 	call factrl
				
! Read the configuration file	
! 	call read_config
	input_model_file = 'helium.mod'
	input_experiment = 'init_parameters.dat'		
	verbose_mode = 0
	linear_solver = 0		
	synthesis_mode = synModeInput
	working_mode = 0
	
! Read the atomic model	
! 	call read_model_file(input_model_file)
	
! Set the variables for the experiment from the parameters of the subroutine
	isti = 1
	imag = 1
	idep = 0
	use_paschen_back = 1
	params%nslabs = nSlabsInput
	if (params%nslabs == 3 .or. params%nslabs == -2) then
		params%bgauss = B1Input(1)
		params%thetabd = B1Input(2)
		params%chibd = B1Input(3)
		params%bgauss2 = B2Input(1)
		params%thetabd2 = B2Input(2)
		params%chibd2 = B2Input(3)
	else
		params%bgauss = B1Input(1)
		params%thetabd = B1Input(2)
		params%chibd = B1Input(3)
	endif
	params%height = hInput
	if (params%nslabs == 1) then
		params%dtau = tau1Input
	endif

	if (params%nslabs == 2 .or. params%nslabs == 3) then
		params%dtau = tau1Input
		params%dtau2 = tau2Input
	endif

! Two components with filling factor
	if (params%nslabs == -2) then
		params%dtau = tau1Input
		params%dtau2 = tau2Input
		params%ff = ffInput
	endif
	
	params%beta = betaInput
	fixed%Stokes_incident = boundaryInput
	fixed%nemiss = transInput
	fixed%use_atomic_pol = atomicPolInput
	fixed%thetad = anglesInput(1)
	fixed%chid = anglesInput(2)
	fixed%gammad = anglesInput(3)
			
	if (params%nslabs == 1 .or. params%nslabs == 2) then
		params%vdopp = dopplerWidthInput
		params%damping = dampingInput
		fixed%damping_treatment = 0
	endif
	if (params%nslabs == 3 .or. params%nslabs == -2) then
		params%vdopp = dopplerWidthInput
		params%vdopp2 = dopplerWidth2Input
		params%damping = dampingInput
		fixed%damping_treatment = 0
	endif
	
! Read the wavelength of the transition that we want to synthesize
	open(unit=12,file=input_model_file,action='read',status='old')
	call lb(12,file_pointer)
	read(12,*) ntran
	do i = 1, transInput
		read(12,*) n, nterml, ntermu, ae, wavelength, &
			reduction_factor, reduction_factor_omega, j10
	enddo
	fixed%wl = wavelength
	close(12)
	
! Set the values of nbar and omega in case they are given
	nbarExternal = nbarInput
	omegaExternal = omegaInput
			
	if (params%nslabs == 1) then
		params%vmacro = dopplerVelocityInput
	else
		params%vmacro = dopplerVelocityInput
		params%vmacro2 = dopplerVelocity2Input
	endif
	
	use_mag_opt_RT = 1
	use_stim_emission_RT = 1	
	
	
!*********************************
!** SYNTHESIS MODE
!*********************************	
	fixed%no = nLambdaInput
	observation%n = fixed%no
	
	allocate(observation%wl(observation%n))
	allocate(inversion%stokes_unperturbed(0:3,fixed%no))
	
	observation%wl = lambdaAxisInput

	call do_synthesis(params, fixed, observation, inversion%stokes_unperturbed)
	
	do i = 1, 4
		stokesOutput(i,:) = inversion%stokes_unperturbed(i-1,:)
	enddo
	
	wavelengthOutput = observation%wl + fixed%wl
	
! Fill the emission vector and absorption matrix
	do i = 1, 4
		epsOutput(i,:) = epsilon(i-1,:)
	enddo
		
	etaOutput(1,1,:) = eta(0,:) - eta_stim(0,:)
	etaOutput(2,2,:) = eta(0,:) - eta_stim(0,:)
	etaOutput(3,3,:) = eta(0,:) - eta_stim(0,:)
	etaOutput(4,4,:) = eta(0,:) - eta_stim(0,:)
	etaOutput(1,2,:) = eta(1,:) - eta_stim(1,:)
	etaOutput(2,1,:) = eta(1,:) - eta_stim(1,:)		
	etaOutput(1,3,:) = eta(2,:) - eta_stim(2,:)
	etaOutput(3,1,:) = eta(2,:) - eta_stim(2,:)
	etaOutput(1,4,:) = eta(3,:) - eta_stim(3,:)
	etaOutput(4,1,:) = eta(3,:) - eta_stim(3,:)
	etaOutput(2,3,:) = mag_opt(3,:) - mag_opt_stim(3,:)
	etaOutput(3,2,:) = -mag_opt(3,:) - mag_opt_stim(3,:)
	etaOutput(2,4,:) = -mag_opt(2,:) - mag_opt_stim(2,:)
	etaOutput(4,2,:) = mag_opt(2,:) - mag_opt_stim(2,:)				 
	etaOutput(3,4,:) = mag_opt(1,:) - mag_opt_stim(1,:)
	etaOutput(4,3,:) = -mag_opt(1,:) - mag_opt_stim(1,:)
	
! 	open(unit=31,file=input_model_file,action='write',status='replace')
! 	close(31,status='delete')
		
end subroutine c_hazel

subroutine c_init() bind(c)
		
! Initialize the random number generator
	call random_seed

! Deallocate memory. Important if we change the number of wavelength points from Python
	if (fixed%no /= size(observation%wl)) then
		if (associated(observation%wl)) deallocate(observation%wl)
		if (associated(inversion%stokes_unperturbed)) deallocate(inversion%stokes_unperturbed)			
	endif

! Initialize Allen's data
	call read_allen_data
		
! Fill the factorial array
	call factrl
				
	input_model_file = 'helium.mod'
	
! Read the atomic model	
	call read_model_file(input_model_file)
	
end subroutine c_init

end module pyHazelMod