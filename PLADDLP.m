function y = PLADDLP()

% length = [2 1;1 3]; %length(i,j) represent length of job j on machine i
% T = 3; %later we use T+1 since I follow the formulation but MATLAB use one base indexing
% K = 2; %number of synch. points; take at time 0 is counted here; 

% length = [1 2;2 1]; %length(i,j) represent length of job j on machine i
% T = 2; %later we use T+1 since I follow the formulation but MATLAB use one base indexing
% K = 2; %number of synch. points; take at time 0 is counted here; 

% length = [1 2 1;1 1 3;5 1 2]; %length(i,j) represent length of job j on machine i
% T = 4; %later we use T+1 since I follow the formulation but MATLAB use one base indexing
% K = 3; %number of synch. points; take at time 0 is counted here; 

% length = [1 2 1;2 1 3]; %length(i,j) represent length of job j on machine i
% T = 4; %later we use T+1 since I follow the formulation but MATLAB use one base indexing
% K = 3; %number of synch. points; take at time 0 is counted here; 

% different input:
% length = [1 2;1 1];
% T = 2;
% K = 3; 

M = size(length,1); %number of servers or number of rows in matrix length
N = size(length,2); %number of jobs on each server or number of columns

L = sum(length,2);
Lmax = max(L);

cvx_begin
variable z(M,T+1) nonnegative
variable x(N,T+Lmax+1,M) nonnegative
variable y(T+1) nonnegative
variable temp3(M,T+1,N)

minimize sum(sum(z))
subject to

%Every job is scheduled:
for m = 1:M
    sum(x(:,:,m),2) == ones(N,1)
end

    
%For a job j, jobs with a greater index much start after j ends    
for m = 1:M
    for i = 1:N
        for j = 1:N
            if i>j
                for t = 1:T+1+L(m)
                    temp4 = min([T+1+L(m) t+length(m,j)-1]);
                    x(j,t,m) + sum(x(i,1:temp4,m)) <= 1
                end
            end
        end
    end
end

%Jobs with an index less than j must end before j starts
for m = 1:M
    for i = 1:N
        for j = 1:N
            if i<j
                for t = 1:T+1+L(m)
                    temp1 = max([1 t-length(m,i)+1]);
                    x(j,t,m) + sum(x(i,temp1:T+L(m)+1,m)) <= 1
%                     mijttemp4 = [m i j t temp1:T+L(m)+1]
                end
            end
        end
    end
end

%Calculation idle time
for m = 1:M
    for t = 1:T+1
        for i = 1:N
            temp2 = max([1 t-length(m,i)+1]);
%             itemp = [i temp2:t]
            temp3(m,t,i) == sum(x(i,temp2:t,m))
        end
        z(m,t)+sum(temp3(m,t,:)) >= 1
    end
end

%Jobs may only start at the takes, which are budgeted
for m = 1:M
    for t = 1:T+1
        sum(x(:,t,m)) <= y(t)
    end
end
sum(y) <= K

y(1) == 1;
% y(2) == 1;
% y(3) == 1;


var_y = y;
var_z = z;
var_x = x;
cvx_end

%printing variables
var_x
var_z
var_y

end