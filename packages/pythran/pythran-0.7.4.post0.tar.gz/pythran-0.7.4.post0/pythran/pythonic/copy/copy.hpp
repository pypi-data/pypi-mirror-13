#ifndef PYTHONIC_COPY_COPY_HPP
#define PYTHONIC_COPY_COPY_HPP

#include "pythonic/utils/int_.hpp"
#include "pythonic/types/traits.hpp"

namespace pythonic
{

  namespace copy
  {
    namespace
    {
      template <class T>
      T _copy(T value, utils::int_<1>)
      {
        return value;
      }
      template <class T>
      auto _copy(T &&value, utils::int_<0>)
          -> decltype(std::forward<T>(value).copy())
      {
        return std::forward<T>(value).copy();
      }
    }

    template <class T>
    auto copy(T &&value) -> decltype(_copy(
        std::forward<T>(value),
        utils::int_<
            types::is_dtype<typename std::remove_reference<T>::type>::value>()))
    {
      return _copy(std::forward<T>(value),
                   utils::int_<types::is_dtype<
                       typename std::remove_reference<T>::type>::value>());
    }

    PROXY(pythonic::copy, copy);
  }
}

#endif
