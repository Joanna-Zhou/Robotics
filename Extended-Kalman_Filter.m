%% Extended Kalman Filter with uniform distribution parameter r = 1, 2.5, 10

clc
clear all

for r = [1, 2.5, 10]
    % Constants
    h = 20;
    d = 200;
    P = 500;
    phi_des = 0;
    cap = 400; % Prevent infinite loop
    
    % Covariances (Constant in this case)
    Q = r^2/3;
    R = h^2 * r^2 / (3 * d^4);

    % To record the path and graph
    X_EKF = []; % With EKF
    X_noKF = []; % Without EKF
    X = []; % Without noise
    K = [];

    % Initial conditions for state model
    x_curr = 100;
    x_noKF = 100;
    x = 100;
    phi_curr = atan(h/(d-x_curr));

    % Initial conditions for measurement model
    P_curr = 0;

    % Counter for preventing infinite loop
    i = 0;
    k = 0;

    % State model update
    while i < cap
        % Append the values each phi_k, x_curr, and k into the group for graphing
        X_EKF = [X_EKF, x_curr];
        X_noKF = [X_noKF, x_noKF];
        X = [X, x];
        K = [K, k];

        % State estimation
        phi_input = x_curr * h / d^2;
        u_k = -P*(phi_input - phi_des); % Control input
        x_est = x_curr + u_k;
        
        % Covariance estimation
        D = h^2 / ((d - x_est)^2 + h^2);
        P_est = P_curr + Q;
        S = D * P_est * D + R; 
        if S == 0
            W = 0;
        else
            W = P_est * D / S; 
        end

        % State update
        phi_est = D * x_est;
        phi_noise = 2 * r * h * rand(1) / d^2 - r * h / d^2; % Measurement error from uniform distribution
        x_curr = x_est + W * (phi_noise);
        phi_curr = phi_est;

        % Covariance update
        P_curr = P_est - W * S * W;
        
        % No Kalman Filter version
        x_noise = 2 * r * rand(1) - r;
        u_k_noKF = -P * ((x_noKF+x_noise) * h / d^2 - phi_des);
        x_noKF = x_noKF + u_k_noKF;
        
        % No Noise version
        u = -P*(x * h / d^2 - phi_des); % Control input
        x = x + u;

        i = i + 1;
        k = k + 1;
    end
    
    
    if r == 1
        subplot(1, 3, 1)
        plot(K, X, K, X_noKF, K, X_EKF, 'linewidth', 1.5);
        xlabel('k');
        ylabel('x [m]');
        title('State x through k steps, with r = 1');
        legend('No Noise', 'No Kalman Filter', 'Extended Kalman Filter');
        x1 = std(X- X_EKF);
        disp(x1)
    end
    if r == 2.5
        subplot(1, 3, 2)
        plot(K, X, K, X_noKF, K, X_EKF, 'linewidth', 1.5);
        xlabel('k');
        ylabel('x [m]');
        title('State x through k steps, with r = 2.5');
        legend('No Noise', 'No Kalman Filter', 'Extended Kalman Filter');
        x2 = std(X- X_EKF);
        disp(x2)
    end
    if r == 10
        subplot(1, 3, 3)
        plot(K, X, K, X_noKF, K, X_EKF, 'linewidth', 1.5);
        xlabel('k');
        ylabel('x [m]');
        title('State x through k steps, with r = 10');
        legend('No Noise', 'No Kalman Filter', 'Extended Kalman Filter');
        x3 = std(X- X_EKF);
        disp(x3)
    end
end
