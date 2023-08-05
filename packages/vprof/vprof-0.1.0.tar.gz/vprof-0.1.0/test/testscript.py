# def lst(size):
    # return ['a' for _ in range(size)]

# lst(1000)

# def prod(lst):
    # if not lst:
        # return 1
    # return lst[0] * prod(lst[1:])

# print(prod(list(range(1, 200))))


# def foo():
#     pass
#     # for _ in range(200):
#         # x = 1
#
# def fib(n):
#     a, b = 0, 1
#     for _ in range(n):
#         foo()
#         yield a
#         a, b = b, a + b
#
# def main():
#     print(list(fib(10)))
#
# if __name__ == "__main__":
#     main()


# def bsearch(lst, el):
#     """Iterative binary search.
#         >>> bsearch([12, 15, 17, 19], 15)
#         1
#         >>> bsearch([1, 2, 3, 4], 3)
#         2
#         >>> bsearch([1, 3, 5, 8, 9, 11], 7)
#     """
#     start, end = 0, len(lst) - 1
#     while start < end:
#         mid = (start + end) // 2
#         if lst[mid] == el:
#             return mid
#         elif el > lst[mid]:
#             start = mid + 1
#         else:
#             end = mid


# def bsearchr(lst, el):
#     """Recursive binary search.
#         >>> bsearchr([12, 15, 17, 19], 15)
#         1
#         >>> bsearchr([1, 2, 3, 4], 3)
#         2
#         >>> bsearchr([1, 3, 5, 8, 9, 11], 7)
#     """
#     def _bsearchr(lst, el):
#         if len(lst) < 2:
#             raise StopIteration
#         mid = len(lst) // 2
#         if lst[mid] == el:
#             return mid
#         elif el > lst[mid]:
#             return _bsearchr(lst[:mid], el)
#         else:
#             return mid + _bsearchr(lst[mid:], el)
#
#     try:
#         return _bsearchr(lst, el)
#     except StopIteration:
#         return
#
#
# for i in range(250):
#     print(bsearchr([1, 2, 3, 4], 3))

#
# def insertion_sort(lst):
#     """ Implementation of insertion sort.
#         >>> insertion_sort([3, 2, 1, 5, 4])
#         [1, 2, 3, 4, 5]
#     """
#     for i, _ in enumerate(lst):
#         for j in range(i, 0, -1):
#             if lst[j] < lst[j - 1]:
#                 lst[j], lst[j - 1] = lst[j - 1], lst[j]
#             else:
#                 break
#     return lst
#
# print(insertion_sort(list(reversed(range(1000)))))

#
#
# def qsort(lst):
#     """Simplest implementation of quicksort.
#        >>> qsort([3, 4, 1, 5, 2, 9, 7, 6, 43, 11])
#        [1, 2, 3, 4, 5, 6, 7, 9, 11, 43]
#     """
#     if not len(lst):
#         return []
#     else:
#         pivot, other = lst[0], lst[1:]
#         lesser = qsort([el for el in other if el < pivot])
#         greater = qsort([el for el in other if el >= pivot])
#         return lesser + [pivot] + greater
#
#
# print(qsort([3, 4, 1, 5, 2, 9, 7, 6, 43, 11]))
#
class DLLNode:
    def __init__(self, value, prev=None, nnext=None):
        self.value, self.prev, self.nnext = value, prev, nnext


class DLL:
    def __init__(self):
        self.head, self.tail = None, None

    def push_back(self, value):
        if not self.head:
            newnode = DLLNode(value)
            self.head, self.tail = newnode, newnode
        else:
            newnode = DLLNode(value, prev=self.tail)
            self.tail.nnext = newnode
            self.tail = newnode

    def push_front(self, value):
        if not self.head:
            newnode = DLLNode(value)
            self.head, self.tail = newnode, newnode
        else:
            newnode = DLLNode(value, nnext=self.head)
            self.head.prev = newnode
            self.head = newnode

    def __iter__(self):
        current = self.head
        while current:
            yield current.value
            current = current.nnext

    def reverse(self):
        first, last = self.tail, self.head
        while first is not last:
            first.value, last.value = last.value, first.value
            first, last = first.prev, last.nnext


import unittest


class DLLUnittest(unittest.TestCase):
    def setUp(self):
        self.dll = DLL()

    def testPushBack(self):
        self.dll.push_back(1)
        self.dll.push_back(3)
        self.dll.push_back(5)
        self.dll.push_back(7)
        self.dll.push_back(9)
        self.assertListEqual(list(self.dll), [1, 3, 5, 7, 9])

    def testPushFront(self):
        self.dll.push_front(1)
        self.dll.push_front(3)
        self.dll.push_front(5)
        self.dll.push_front(7)
        self.dll.push_front(9)
        self.assertListEqual(list(self.dll), [9, 7, 5, 3, 1])

    def testReverse(self):
        self.dll.push_front(1)
        self.dll.push_front(3)
        self.dll.push_front(5)
        self.dll.push_front(7)
        self.dll.push_front(9)
        self.dll.reverse()
        self.assertListEqual(list(self.dll), [1, 3, 5, 7, 9])

    def testMixed(self):
        self.dll.push_front(1)
        self.dll.push_back(3)
        self.dll.push_front(5)
        self.dll.push_back(7)
        self.dll.push_back(9)
        self.assertListEqual(list(self.dll), [5, 1, 3, 7, 9])


# if __name__ == "__main__":
unittest.main()
# #
# # # import urllib

# response = urllib.urlopen('http://google.com/')
# for line in response:
#     print line.rstrip()




# import numpy
# import scipy.io
# import scipy.optimize
# import pylab
#
# def linear_kernel(x, theta):
#     """ Linear kernel for SVM """
#     return x * numpy.transpose(theta)
#
# def gaussian_kernel(x, theta):
#     pass
#
# def cost_function(theta, x, y, c):
#     """ Cost function for SVM """
#     # print theta
#     theta = numpy.matrix(theta)
#     cost = (c * (numpy.transpose(y) * linear_kernel(x, theta) +
#             (1.0 - numpy.transpose(y)) * linear_kernel(x, theta))
#              + 0.5 * numpy.sum(numpy.power(theta, 2)))
#     #print cost
#     return cost
#
# def optimizer(x, y, c):
#     """ Optimization of SVM's cost function """
#     m = len(x)
#     xs = numpy.matrix(numpy.vstack((numpy.ones((1, m)), numpy.transpose(x)))).transpose()
#     ys = numpy.matrix(y)
#     init_theta = numpy.matrix(numpy.zeros((1, x.shape[1] + 1)))
#     # print init_theta
#     return scipy.optimize.fmin(cost_function, init_theta, args=(xs, ys, c))
#
# def evaluate_svm(x, theta):
#     """ Evaluate SVM """
#     m = len(x)
#     thetas = numpy.matrix(theta)
#     xs = numpy.matrix(numpy.vstack((numpy.ones((1, m)), numpy.transpose(x)))).transpose()
#     return xs * numpy.transpose(thetas)
#
#
# # with open('data/ex6data1.mat') as datafile:
# data = scipy.io.loadmat('test/ex6data1.mat')
# thetas = optimizer(data['X'], data['y'], 0.001)
# x1, x2, y = data['X'][:, 0], data['X'][:, 1], data['y']
# positive_x1, positive_x2 = x1[(y==1).flatten()], x2[(y==1).flatten()]
# negative_x1, negative_x2 = x1[(y==0).flatten()], x2[(y==0).flatten()]
# pylab.plot(positive_x1, positive_x2, 'rs', label='Positive')
# pylab.plot(negative_x1, negative_x2, 'go', label='Negative')
# min_x1, max_x1  = x1.min(), x1.max()
# min_x2, max_x2  = x2.min(), x2.max()
# x1p, x2p = numpy.linspace(min_x1, max_x1, 50), numpy.linspace(min_x2, max_x2, 50)
# yp = numpy.empty((len(x1p), len(x2p)))
# for i, x1 in enumerate(x1p):
#     for j, x2 in enumerate(x2p):
#         yp[i][j] = thetas[0] + x1 * thetas[1] + x2 * thetas[2]
# pylab.contour(x1p, x2p, yp, [0], label='Decision boundary')
# pylab.xlabel('Feature 1')
# pylab.ylabel('Feature 2')
# pylab.legend()
#pylab.show()
